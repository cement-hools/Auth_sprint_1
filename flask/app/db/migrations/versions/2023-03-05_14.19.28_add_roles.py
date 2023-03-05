"""add_roles

Revision ID: 7aaa02dfbf63
Revises: 01d6985a9138
Create Date: 2023-03-05 14:19:28.306613

"""
from alembic import op
import sqlalchemy as sa

from app.db import db
from app.db.models import Role
from app.settings.core import UserRoles

# revision identifiers, used by Alembic.
revision = '7aaa02dfbf63'
down_revision = '01d6985a9138'
branch_labels = None
depends_on = None

roles_config = UserRoles()

def upgrade():
    role_admin = Role(name=roles_config.admin, description="Big boss")
    role_user = Role(name=roles_config.user, description="Regular user")
    db.session.add(role_admin)
    db.session.add(role_user)
    db.session.commit()


def downgrade():
    roles = [roles_config.admin, roles_config.user]
    db.session.query(Role).filter(Role.name.in_(roles)).delete()
    db.session.commit()

