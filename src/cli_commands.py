import click
from flask.cli import with_appcontext

from app.db import db
from app.db.models.role import Role
from app.db.models.user import User
from settings import user_roles_settings


@click.command("create_user")
@click.argument("login")
@click.argument("email")
@click.argument("password")
@click.option("--admin", is_flag=True, help="Make the user an admin")
@with_appcontext
def create_user(login, email, password, admin=False):
    """Create a user."""
    user = User.query.filter_by(email=email).first()
    if user is not None:
        click.echo("User with email {} already exists.".format(email))
        return

    if admin:
        role_id = user_roles_settings.uuids["admin"]
    else:
        role_id = user_roles_settings.uuids["user"]
    role = Role.query.filter_by(id=role_id).first()
    if role is None:
        click.echo("Role not found")
        return

    user = User(login=login, email=email, password=password, roles=[role])
    db.session.add(user)
    db.session.commit()
    click.echo("User created successfully.")
