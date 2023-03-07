"""add_social_name_type

Revision ID: f12e4922ee91
Revises: 7aaa02dfbf63
Create Date: 2023-03-07 09:36:18.164713

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f12e4922ee91"
down_revision = "7aaa02dfbf63"
branch_labels = None
depends_on = None


SOCIAL_NAME_TYPE = sa.Enum("yandex", "google", name="social_name_type")
SOCIAL_NAME_TYPE_PG = postgresql.ENUM(
    "yandex", "google", name="social_name_type"
)

SOCIAL_NAME_TYPE.with_variant(SOCIAL_NAME_TYPE_PG, "postgresql")


def upgrade():
    SOCIAL_NAME_TYPE.create(op.get_bind(), checkfirst=True)


def downgrade():
    SOCIAL_NAME_TYPE.drop(op.get_bind(), checkfirst=False)
