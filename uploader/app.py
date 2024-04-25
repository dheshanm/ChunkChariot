#!/usr/bin/env python
"""
Implements a simple file server that allows users to upload files to the server.
"""

import sys
from pathlib import Path

file = Path("/Users/dm1447/dev/web/uploader/uploader/app.py")
parent = file.parent
ROOT = None
for parent in file.parents:
    if parent.name == "uploader":
        ROOT = parent
sys.path.append(str(ROOT))

import logging
from typing import Optional

import flask
import flask_login
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect

from uploader import orchestrator
from uploader.helpers import utils, cli
from uploader.models.user import User

MODULE_NAME = "uploader.app"

logger = logging.getLogger(MODULE_NAME)
logargs = {
    "level": logging.DEBUG,
    "format": "%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s",
    # "format": "%(message)s",
}
logging.basicConfig(**logargs)


app: Optional[flask.Flask] = None
login_manager: Optional[flask_login.LoginManager] = None


def create_app(config_file: Path) -> flask.Flask:
    """
    Creates a Flask app.

    Args:
        config_file (Path): The path to the config file.

    Returns:
        flask.Flask: The Flask app.
    """
    global app, login_manager  # pylint: disable=global-statement
    app = flask.Flask(__name__)
    login_manager = flask_login.LoginManager()

    @login_manager.user_loader
    def load_user(user_email: User) -> Optional[User]:
        """
        Loads a user from the database.

        Args:
            user (User): The user object.

        Returns:
            User: The user object.
        """
        logger.debug(f"Loading user: {user_email}")
        return User.find_by_email_query(user_email)  # type: ignore

    storage_path = orchestrator.get_storage_path(config_file=config_file)
    chunk_path = orchestrator.get_chunk_path(config_file=config_file)
    hostname = cli.get_hostname()

    logger.info(f"Using storage path: {storage_path}")
    logger.info(f"Using chunk path: {chunk_path}")

    app.secret_key = orchestrator.get_secret_key(config_file=config_file)
    app.config["STORAGE_PATH"] = str(storage_path)
    app.config["CHUNK_PATH"] = str(chunk_path)
    app.config["HOSTNAME"] = hostname

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore

    from uploader.blueprints.auth import (  # pylint: disable=import-outside-toplevel
        auth_bp,
    )

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from uploader.blueprints.healthcheck import (  # pylint: disable=import-outside-toplevel
        healthcheck_bp,
    )

    app.register_blueprint(healthcheck_bp, url_prefix="/")

    from uploader.blueprints.upload import (  # pylint: disable=import-outside-toplevel
        upload_bp,
    )

    app.register_blueprint(upload_bp, url_prefix="/upload")

    @app.route("/favicon.ico")
    def favicon():
        # send favicon from static folder
        return flask.send_from_directory(
            app.root_path + "/static",
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
            max_age=86400,
        )

    return app


if __name__ == "__main__":
    config_file = utils.get_config_file_path()
    logger.info(f"Using config file: {config_file}")

    utils.configure_logging(
        config_file=config_file, module_name=MODULE_NAME, logger=logger
    )

    app = create_app(config_file=config_file)

    bootstrap = Bootstrap5(app)
    csrf = CSRFProtect(app)

    app.run(debug=True, port=15000, host="0.0.0.0")
