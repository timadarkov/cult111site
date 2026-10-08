"""Run: python tests/test_image_settings.py (FastAPI, HTTPX, SQLAlchemy required).
Uses only in-memory SQLite; does not import production settings or connect to R2.
"""
import ast
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
database = ModuleType("database")
database.Base = declarative_base()
config = ModuleType("app.core.config")
config.settings = SimpleNamespace(r2_public_url="https://cdn.test")
with patch.dict(sys.modules, {"database": database, "app.core.config": config}):
    from app.models.brand import Brands
    from app.models.category import Category
    from app.models.image import Images
    from app.models.product import Products
    from app.schemas import image_copy
    from app.services import image_copy_services
    from app.storage import image_copy as image_copy_storage
    from app.schemas import image_settings
    from app.services import image_settings_services


class ImageSettingsTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
        )
        database.Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            db.add_all([Brands(id=1, name="Brand"), Category(id=1, name="Category")])
            db.add_all([
                Products(id=i, name="Product", price=10, description="", category_id=1,
                         brand_id=1, is_visible=False)
                for i in (1, 2)
            ])
            db.add_all([
                Images(id=1, product_id=1, key="products/1", position=0, is_main=True),
                Images(id=2, product_id=1, key="products/2", position=1, is_main=False),
                Images(id=3, product_id=2, key="products/3", position=0, is_main=True),
                Images(id=4, product_id=1, key="products/4", position=2,
                       is_main=False, is_visible=False),
            ])
            db.commit()

        def get_db():
            with Session(self.engine) as db:
                yield db

        # Compile the actual new route functions without importing unrelated
        # production services, settings, credentials or database connections.
        tree = ast.parse((ROOT / "app/api/v1/admin/product.py").read_text())
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name in {"update_main_image", "update_image_order", "copy_product_image"}]
        self.assertEqual(len(functions), 3)
        router = APIRouter(prefix="/api/v1/admin/products")
        namespace = dict(router=router, Session=Session, Depends=Depends, get_db=get_db,
                         image_settings=image_settings,
                         image_settings_services=image_settings_services, image_copy=image_copy,
                         image_copy_services=image_copy_services)
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(ROOT), "exec"), namespace)
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.engine.dispose()

    def state(self):
        with Session(self.engine) as db:
            return [(i.id, i.position, i.is_main) for i in db.query(Images).order_by(Images.id)]

    def request(self, action, data, product_id=1):
        return self.client.patch(f"/api/v1/admin/products/{product_id}/images/{action}", json=data)

    def test_main_switch_keeps_order_and_other_product(self):
        response = self.request("main", {"image_id": 2})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.state(), [(1, 0, False), (2, 1, True), (3, 0, True), (4, 2, False)])
        self.assertEqual(self.request("main", {"image_id": 2}).status_code, 204)

    def test_order_keeps_main_and_hidden_images(self):
        self.assertEqual(self.request("order", {"image_ids": [2, 1]}).status_code, 204)
        self.assertEqual(self.state(), [(1, 1, True), (2, 0, False), (3, 0, True), (4, 2, False)])

    def test_invalid_main_leaves_database_unchanged(self):
        before = self.state()
        for image_id in (3, 4, 999):
            self.assertEqual(self.request("main", {"image_id": image_id}).status_code, 404)
            self.assertEqual(self.state(), before)

    def test_invalid_order_leaves_database_unchanged(self):
        before = self.state()
        for ids in ([1], [1, 1], [1, 3], [1, 2, 999], [1, 2, 4], [], [True, 2], ["1", 2], [-1, 2]):
            with self.subTest(ids=ids):
                self.assertEqual(self.request("order", {"image_ids": ids}).status_code, 422)
                self.assertEqual(self.state(), before)

    def test_missing_product(self):
        for action, data in (("main", {"image_id": 1}), ("order", {"image_ids": [1, 2]})):
            self.assertEqual(self.request(action, data, 999).status_code, 404)

    def test_main_validation(self):
        for data in ({}, {"image_id": None}, {"image_id": True}, {"image_id": 0}, {"image_id": "2"}):
            self.assertEqual(self.request("main", data).status_code, 422)

    def test_copy_creates_independent_file_at_end(self):
        with patch.object(image_copy_storage, "copy_image_file") as copy_file:
            response = self.client.post("/api/v1/admin/products/2/images/copy", json={"image_id": 1})
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(result["product_id"], 2)
        self.assertEqual(result["position"], 1)
        self.assertFalse(result["is_main"])
        self.assertNotEqual(result["key"], "products/1")
        self.assertEqual(result["url"], "https://cdn.test/"+result["key"])
        copy_file.assert_called_once_with("products/1", result["key"])
        self.assertEqual(self.state()[:4], [(1, 0, True), (2, 1, False), (3, 0, True), (4, 2, False)])

    def test_first_copy_becomes_main_on_hidden_product(self):
        with Session(self.engine) as db:
            db.add(Products(id=3, name="Empty", price=10, description="", category_id=1, brand_id=1, is_visible=False))
            db.commit()
        with patch.object(image_copy_storage, "copy_image_file"):
            response = self.client.post("/api/v1/admin/products/3/images/copy", json={"image_id": 1})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["is_main"])
        self.assertEqual(response.json()["position"], 0)

    def test_copy_validation_does_not_touch_storage(self):
        before = self.state()
        with patch.object(image_copy_storage, "copy_image_file") as copy_file:
            for product_id, image_id, status in [(1, 1, 409), (2, 4, 404), (2, 999, 404), (999, 1, 404), (2, True, 422)]:
                response = self.client.post(f"/api/v1/admin/products/{product_id}/images/copy", json={"image_id": image_id})
                self.assertEqual(response.status_code, status)
            copy_file.assert_not_called()
        self.assertEqual(self.state(), before)

    def test_storage_failure_leaves_database_unchanged(self):
        before = self.state()
        with patch.object(image_copy_storage, "copy_image_file", side_effect=RuntimeError("Storage unavailable")):
            response = self.client.post("/api/v1/admin/products/2/images/copy", json={"image_id": 1})
        self.assertEqual(response.status_code, 502)
        self.assertEqual(self.state(), before)

    def test_database_failure_removes_new_copy(self):
        before = self.state()
        with Session(self.engine) as db, patch.object(db, "commit", side_effect=RuntimeError("DB unavailable")), patch.object(image_copy_storage, "copy_image_file") as copy_file, patch.object(image_copy_storage, "delete_image_file") as delete_file:
            with self.assertRaises(RuntimeError):
                image_copy_services.copy_product_image(db, 2, image_copy.ImageCopyRequest(image_id=1))
            delete_file.assert_called_once_with(copy_file.call_args.args[1])
        self.assertEqual(self.state(), before)


if __name__ == "__main__":
    unittest.main()
