"""restrict product category and brand deletion

Revision ID: f82024022ef4
Revises: 774f1f4e4462
Create Date: 2026-11-06 21:36:20.196981

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f82024022ef4'
down_revision: Union[str, Sequence[str], None] = '774f1f4e4462'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "products_brand_id_fkey",
        "products",
        type_="foreignkey",
    )
    op.drop_constraint(
        "products_category_id_fkey",
        "products",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "products_brand_id_fkey",
        "products",
        "brands",
        ["brand_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "products_category_id_fkey",
        "products",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "products_brand_id_fkey",
        "products",
        type_="foreignkey",
    )
    op.drop_constraint(
        "products_category_id_fkey",
        "products",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "products_brand_id_fkey",
        "products",
        "brands",
        ["brand_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "products_category_id_fkey",
        "products",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="CASCADE",
    )
