"""add_index_ix_vacancies_id

Revision ID: 841aea2fe835
Revises: bbd0f91a67b5
Create Date: 2025-11-29 21:25:38.501279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '841aea2fe835'
down_revision: Union[str, Sequence[str], None] = 'bbd0f91a67b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = [idx["name"] for idx in inspector.get_indexes("vacancies")]
    
    if "ix_vacancies_id" not in indexes:
        op.create_index(op.f("ix_vacancies_id"), "vacancies", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_vacancies_id"), table_name="vacancies")
