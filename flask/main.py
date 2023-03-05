from gevent import monkey

monkey.patch_all()

from app import create_app  # noqa E402
from app.settings.core import flask_settings  # noqa E402

app = create_app()

if __name__ == "__main__":
    app.run(
        host=flask_settings.host,
        port=flask_settings.port,
        debug=flask_settings.debug,
    )
