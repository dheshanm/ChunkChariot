"""
Heart beat check for the uploader service.
"""

from datetime import datetime

import flask
import flask_login

from uploader.models import Metadata

healthcheck_bp = flask.Blueprint(
    "healthcheck", __name__, url_prefix="/healthcheck", template_folder="templates"
)


@healthcheck_bp.route("/", methods=["GET"])
def healthcheck() -> flask.Response:
    """
    Health (heartbeat) check.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    current_app = flask.current_app
    current_user = flask_login.current_user

    metadata: Metadata = Metadata(flask.request, current_user=current_user)  # type: ignore
    host_name = flask.request.host
    if 'localhost' in host_name:
        real_host_name = current_app.config["HOSTNAME"]
        # replace localhost with the real hostname
        host_name = host_name.replace('localhost', real_host_name)

    return flask.Response(
        flask.render_template(
            "healthcheck.html",
            metadata=metadata,
            title="Home",
            host_name=host_name,
            server_time=current_time,
        )
    )
