from app import create_app
from gevent import monkey
from settings import flask_settings

monkey.patch_all()

app = create_app()

if __name__ == "__main__":
    app.run(
        host=flask_settings.host,
        port=flask_settings.port,
        debug=flask_settings.debug,
    )
