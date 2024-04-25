"""
Heart beat check for the uploader service.
"""

from datetime import datetime

import flask
import flask_login

from uploader.models import Metadata
from uploader import constants

healthcheck_bp = flask.Blueprint(
    "healthcheck", __name__, url_prefix="/healthcheck", template_folder="templates"
)


@healthcheck_bp.route("/", methods=["GET"])
def healthcheck() -> flask.Response:
    """
    Health (heartbeat) check.
    """
    host_name = flask.request.host
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    current_user = flask_login.current_user

    metadata: Metadata = Metadata(flask.request, current_user=current_user)  # type: ignore

    return flask.Response(
        flask.render_template(
            "healthcheck.html",
            metadata=metadata,
            title=constants.APP_NAME,
            host_name=host_name,
            server_time=current_time,
        )
    )
