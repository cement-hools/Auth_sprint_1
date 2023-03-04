import click
from app.db import db
from app.db.models.role import Role
from app.db.models.user import User

from flask.cli import with_appcontext


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
        role_name = "admin"
    else:
        role_name = "user"
    role = Role.query.filter_by(name=role_name).first()
    if role is None:
        click.echo("Role not found")
        return

    user = User(login=login, email=email, password=password, roles=[role])
    db.session.add(user)
    db.session.commit()
    click.echo("User created successfully.")
