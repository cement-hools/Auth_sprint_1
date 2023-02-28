"""add_roles

Revision ID: 2e0dd64bdd72
Revises: 5e71152c3e76
Create Date: 2023-02-20 11:27:22.184479

"""

from app.db import db
from app.db.models import Role

# revision identifiers, used by Alembic.
revision = "2e0dd64bdd72"
down_revision = "5e71152c3e76"
branch_labels = None
depends_on = None


def upgrade():
    role_admin = Role(name="admin", description="Big boss")
    role_user = Role(name="user", description="Regular user")
    db.session.add(role_admin)
    db.session.add(role_user)
    db.session.commit()


def downgrade():
    db.session.query(Role).filter(Role.name.in_(["admin", "user"])).delete()
    db.session.commit()
