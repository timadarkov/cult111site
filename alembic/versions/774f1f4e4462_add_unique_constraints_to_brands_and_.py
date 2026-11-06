"""add unique constraints to brands and categories

Revision ID: 774f1f4e4462
Revises: e057fa9e6018
Create Date: 2026-11-06 21:09:37.775900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '774f1f4e4462'
down_revision: Union[str, Sequence[str], None] = 'e057fa9e6018'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_brands_name", "brands", ["name"]
    )
    op.create_unique_constraint(
        "uq_categories_name", "categories", ["name"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_categories_name", "categories", type_="unique"
    )
    op.drop_constraint(
        "uq_brands_name", "brands", type_="unique"
    )
