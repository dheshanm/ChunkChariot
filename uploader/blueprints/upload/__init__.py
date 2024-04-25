"""
Allows uploading files.
"""

# References:
# https://codecalamity.com/upload-large-files-fast-with-dropzone-js/
# https://codecalamity.com/uploading-large-files-by-chunking-featuring-python-flask-and-dropzone-js/
# https://stackoverflow.com/questions/44727052/handling-large-file-uploads-with-flask

import collections
import logging
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import DefaultDict, List

import flask
import flask_login
from werkzeug import utils as werkzeug_utils

from uploader.blueprints.upload.models import UploadForm
from uploader.models import Metadata
from uploader.helpers import cli
from uploader.models.user import User

logger = logging.getLogger(__name__)

lock = threading.Lock()
chucks: DefaultDict[str, List[int]] = collections.defaultdict(list)

upload_bp = flask.Blueprint(
    "upload", __name__, url_prefix="/upload", template_folder="templates"
)


@upload_bp.route("/", methods=["GET"])
@flask_login.login_required
def upload_file() -> flask.Response:
    """
    Returns a form to upload a file.

    Returns:
        flask.Response: A response object.
    """
    metadata: Metadata = Metadata(flask.request)
    current_user: User = flask_login.current_user  # type: ignore

    if flask.request.method == "GET":
        form = UploadForm()

        form.date_uploaded.data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        form.uploaded_by.data = current_user.username

        return flask.Response(
            flask.render_template(
                "form.html", metadata=metadata, title="Upload", form=form
            )
        )

    return flask.Response(
        status=405,
        response="Method Not Allowed",
    )


@upload_bp.route("/upload", methods=["POST"])
@flask_login.login_required
def upload() -> flask.Response:
    """
    Uploads a file to the server.

    Returns:
        flask.Response: A response object.
    """

    file = flask.request.files.get("file")
    if not file:
        return flask.Response(
            status=301,
            response="No file provided",
        )

    storage_path = Path(flask.current_app.config["STORAGE_PATH"])
    chunk_path = Path(flask.current_app.config["CHUNK_PATH"])

    dz_uuid = flask.request.form.get("dzuuid")
    if not dz_uuid:
        # Assume this file has not been chunked
        file_path = storage_path / f"{uuid.uuid4()}_{werkzeug_utils.secure_filename(file.filename)}"  # type: ignore
        with open(file_path, "wb") as f:
            file.save(f)
        return flask.Response(
            status=200,
            response="File uploaded successfully",
        )

    # Chunked download
    try:
        current_chunk = int(flask.request.form["dzchunkindex"])
        total_chunks = int(flask.request.form["dztotalchunkcount"])
    except KeyError as err:
        return flask.Response(
            status=400,
            response=f"Missing key {err}",
        )
    except ValueError:
        return flask.Response(
            status=400,
            response="Invalid chunk index or total count",
        )

    # Save chunks in a directory named after the dz_uuid
    # This is to avoid conflicts when multiple files are being uploaded
    #
    # The directory will be deleted once all the chunks are downloaded
    save_dir = chunk_path / dz_uuid

    if not save_dir.exists():
        save_dir.mkdir(exist_ok=True, parents=True)

    # Save the individual chunk
    with open(save_dir / str(flask.request.form["dzchunkindex"]), "wb") as f:
        file.save(f)

    # See if we have all the chunks downloaded
    with lock:
        chucks[dz_uuid].append(current_chunk)
        completed = len(chucks[dz_uuid]) == total_chunks

    # Concat all the files into the final file when all are downloaded
    if completed:
        file_path = storage_path / f"{dz_uuid}_{werkzeug_utils.secure_filename(file.filename)}"  # type: ignore
        with open(file_path, "wb") as f:
            for file_number in range(total_chunks):
                f.write((save_dir / str(file_number)).read_bytes())
        logger.info(f"{file.filename} has been uploaded")

        cli.remove_directory(save_dir)

    return flask.Response(
        status=200,
        response="Chunk uploaded successfully",
    )
