from gevent import monkey

from app import create_app
from app.api.v1.utils import after_request_log, before_request_log
from settings import flask_settings

monkey.patch_all()

app = create_app()
app.before_request(before_request_log)
app.after_request(after_request_log)

if __name__ == "__main__":
    app.run(
        host=flask_settings.host,
        port=flask_settings.port,
        debug=flask_settings.debug,
    )
