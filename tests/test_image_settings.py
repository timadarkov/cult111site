"""Run: poetry run pytest tests/test_image_settings.py.
Uses in-memory SQLite with aiosqlite.
"""

import ast
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from fastapi import APIRouter, Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from app.schemas import image as image_schema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

database = ModuleType("database")
database.Base = declarative_base()

config = ModuleType("app.core.config")
config.settings = SimpleNamespace(
    r2_public_url="https://cdn.test"
)

with patch.dict(
    sys.modules,
    {"database": database, "app.core.config": config},
):
    from app.models.brand import Brands
    from app.models.category import Category
    from app.models.image import Images
    from app.models.product import Products
    from app.schemas import image_copy, image_settings
    from app.services import (
        image_copy_services,
        image_settings_services,
    )
    from app.storage import image_copy as image_copy_storage


class ImageSettingsTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.engine = create_async_engine(
            "sqlite+aiosqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        async with self.engine.begin() as connection:
            await connection.run_sync(
                Brands.__table__.metadata.create_all
            )

        async with AsyncSession(
            self.engine,
            expire_on_commit=False,
        ) as db:

            db.add_all([
                Brands(id=1, name="Brand"),
                Category(id=1, name="Category"),
            ])

            db.add_all([
                Products(
                    id=i,
                    name="Product",
                    price=10,
                    description="",
                    category_id=1,
                    brand_id=1,
                    is_visible=False,
                )
                for i in (1, 2)
            ])

            db.add_all([
                Images(
                    id=1,
                    product_id=1,
                    key="products/1",
                    position=0,
                    is_main=True,
                ),
                Images(
                    id=2,
                    product_id=1,
                    key="products/2",
                    position=1,
                    is_main=False,
                ),
                Images(
                    id=3,
                    product_id=2,
                    key="products/3",
                    position=0,
                    is_main=True,
                ),
                Images(
                    id=4,
                    product_id=1,
                    key="products/4",
                    position=2,
                    is_main=False,
                    is_visible=False,
                ),
            ])

            await db.commit()

        async def get_db():
            async with AsyncSession(
                self.engine,
                expire_on_commit=False,
            ) as db:
                yield db

        tree = ast.parse(
            (ROOT / "app/api/v1/admin/product.py").read_text()
        )

        functions = [
            node
            for node in tree.body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name in {
                "update_main_image",
                "update_image_order",
                "copy_product_image",
            }
        ]

        self.assertEqual(len(functions), 3)

        router = APIRouter(prefix="/api/v1/admin/products")

        namespace = dict(
            router=router,
            AsyncSession=AsyncSession,
            Depends=Depends,
            get_db=get_db,
            image_settings=image_settings,
            image_settings_services=image_settings_services,
            image_copy=image_copy,
            image_copy_services=image_copy_services,
        )

        exec(
            compile(
                ast.Module(body=functions, type_ignores=[]),
                str(ROOT),
                "exec",
            ),
            namespace,
        )

        app = FastAPI()
        app.include_router(router)

        self.client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        )

    async def asyncTearDown(self):
        try:
            await self.client.aclose()
        finally:
            await self.engine.dispose()

    async def state(self):
        async with AsyncSession(self.engine) as db:
            stmt = select(Images).order_by(Images.id)
            result = await db.execute(stmt)

            return [
                (i.id, i.position, i.is_main)
                for i in result.scalars().all()
            ]

    async def request(self, action, data, product_id=1):
        return await self.client.patch(
            f"/api/v1/admin/products/{product_id}/images/{action}",
            json=data,
        )

    async def test_main_switch_keeps_order_and_other_product(self):
        response = await self.request("main", {"image_id": 2})

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")

        self.assertEqual(
            await self.state(),
            [(1, 0, False), (2, 1, True), (3, 0, True), (4, 2, False)],
        )

        self.assertEqual(
            (await self.request("main", {"image_id": 2})).status_code,
            204,
        )

    async def test_order_keeps_main_and_hidden_images(self):
        self.assertEqual(
            (await self.request("order", {"image_ids": [2, 1]})).status_code,
            204,
        )

        self.assertEqual(
            await self.state(),
            [(1, 1, True), (2, 0, False), (3, 0, True), (4, 2, False)],
        )

    async def test_invalid_main_leaves_database_unchanged(self):
        before = await self.state()

        for image_id in (3, 4, 999):
            self.assertEqual(
                (await self.request("main", {"image_id": image_id})).status_code,
                404,
            )

            self.assertEqual(await self.state(), before)

    async def test_invalid_order_leaves_database_unchanged(self):
        before = await self.state()

        for ids in (
            [1],
            [1, 1],
            [1, 3],
            [1, 2, 999],
            [1, 2, 4],
            [],
            [True, 2],
            ["1", 2],
            [-1, 2],
        ):
            with self.subTest(ids=ids):
                self.assertEqual(
                    (await self.request("order", {"image_ids": ids})).status_code,
                    422,
                )

                self.assertEqual(await self.state(), before)

    async def test_missing_product(self):
        for action, data in (
            ("main", {"image_id": 1}),
            ("order", {"image_ids": [1, 2]}),
        ):
            self.assertEqual(
                (await self.request(action, data, 999)).status_code,
                404,
            )

    async def test_main_validation(self):
        for data in (
            {},
            {"image_id": None},
            {"image_id": True},
            {"image_id": 0},
            {"image_id": "2"},
        ):
            self.assertEqual(
                (await self.request("main", data)).status_code,
                422,
            )

    async def test_copy_creates_independent_file_at_end(self):
        with (
            patch.object(image_schema, "settings", config.settings),
            patch.object(image_copy_storage, "copy_image_file") as copy_file,
        ):
            response = await self.client.post(
                "/api/v1/admin/products/2/images/copy",
                json={"image_id": 1},
            )

        self.assertEqual(response.status_code, 201)

        result = response.json()

        self.assertEqual(result["product_id"], 2)
        self.assertEqual(result["position"], 1)
        self.assertFalse(result["is_main"])
        self.assertNotEqual(result["key"], "products/1")
        self.assertEqual(
            result["url"],
            "https://cdn.test/" + result["key"],
        )

        copy_file.assert_called_once_with(
            "products/1",
            result["key"],
        )

        self.assertEqual(
            (await self.state())[:4],
            [(1, 0, True), (2, 1, False), (3, 0, True), (4, 2, False)],
        )

    async def test_first_copy_becomes_main_on_hidden_product(self):
        async with AsyncSession(self.engine) as db:
            db.add(
                Products(
                    id=3,
                    name="Empty",
                    price=10,
                    description="",
                    category_id=1,
                    brand_id=1,
                    is_visible=False,
                )
            )

            await db.commit()

        with patch.object(image_copy_storage, "copy_image_file"):
            response = await self.client.post(
                "/api/v1/admin/products/3/images/copy",
                json={"image_id": 1},
            )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["is_main"])
        self.assertEqual(response.json()["position"], 0)

    async def test_copy_validation_does_not_touch_storage(self):
        before = await self.state()

        with patch.object(
            image_copy_storage,
            "copy_image_file",
        ) as copy_file:

            for product_id, image_id, status in [
                (1, 1, 409),
                (2, 4, 404),
                (2, 999, 404),
                (999, 1, 404),
                (2, True, 422),
            ]:
                response = await self.client.post(
                    f"/api/v1/admin/products/{product_id}/images/copy",
                    json={"image_id": image_id},
                )

                self.assertEqual(response.status_code, status)

            copy_file.assert_not_called()

        self.assertEqual(await self.state(), before)

    async def test_storage_failure_leaves_database_unchanged(self):
        before = await self.state()

        with patch.object(
            image_copy_storage,
            "copy_image_file",
            side_effect=RuntimeError("Storage unavailable"),
        ):
            response = await self.client.post(
                "/api/v1/admin/products/2/images/copy",
                json={"image_id": 1},
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(await self.state(), before)

    async def test_database_failure_removes_new_copy(self):
        before = await self.state()

        async with AsyncSession(self.engine) as db:
            with (
                patch.object(
                    db,
                    "commit",
                    side_effect=RuntimeError("DB unavailable"),
                ),
                patch.object(
                    image_copy_storage,
                    "copy_image_file",
                ) as copy_file,
                patch.object(
                    image_copy_storage,
                    "delete_image_file",
                ) as delete_file,
            ):
                with self.assertRaises(RuntimeError):
                    await image_copy_services.copy_product_image(
                        db,
                        2,
                        image_copy.ImageCopyRequest(image_id=1),
                    )

                delete_file.assert_called_once_with(
                    copy_file.call_args.args[1]
                )

        self.assertEqual(await self.state(), before)


if __name__ == "__main__":
    unittest.main()
