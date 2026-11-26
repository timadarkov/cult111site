import pytest
from sqlalchemy import event

from app.models.image import Images
from app.schemas.product import ProductAdminResponse
from app.storage.product import get_product_admin


@pytest.mark.parametrize("product_count", [1, 10, 100])
async def test_product_list_no_n_plus_one(
    db_session,
    test_engine,
    brand_factory,
    category_factory,
    product_factory,
    product_count,
):
    brand = await brand_factory("N1 Brand")
    category = await category_factory("N1 Category")

    for i in range(product_count):
        product = await product_factory(
            name=f"Product {i}",
            price=100,
            category_id=category.id,
            brand_id=brand.id,
        )

        db_session.add(
            Images(
                product_id=product.id,
                key=f"products/test-{i}.png",
                position=0,
                is_main=True,
            )
        )

    await db_session.flush()
    db_session.expire_all()

    queries = []

    def count_queries(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            queries.append(statement)

    event.listen(test_engine.sync_engine, "before_cursor_execute", count_queries)

    try:
        products = await get_product_admin(db_session)

        responses = [
            ProductAdminResponse.model_validate(product)
            for product in products
        ]
        assert all(len(response.images) == 1 for response in responses)

    finally:
        event.remove(test_engine.sync_engine, "before_cursor_execute", count_queries)

    assert len(products) == product_count
    assert len(responses) == product_count
    assert len(queries) == 2
