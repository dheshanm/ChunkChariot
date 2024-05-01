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
from pathlib import Path
from typing import DefaultDict, List

import flask
import flask_login
from werkzeug import utils as werkzeug_utils
import pandas as pd

from uploader.blueprints.upload.models import UploadForm
from uploader.models import Metadata
from uploader.helpers import cli
from uploader.models.user import User
from uploader.models.uploaded_file import UploadedFile
from uploader.models.submission import Submission
from uploader.models.submitted_files_map import SubmittedFilesMap
from uploader.blueprints.upload.models import UploadedFileView

logger = logging.getLogger(__name__)

lock = threading.Lock()
chucks: DefaultDict[str, List[int]] = collections.defaultdict(list)

upload_bp = flask.Blueprint(
    "upload", __name__, url_prefix="/upload", template_folder="templates"
)


@upload_bp.route("/", methods=["GET", "POST"])
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

        form.uploaded_by.data = current_user.username

        return flask.Response(
            flask.render_template(
                "form.html",
                metadata=metadata,
                title="Upload",
                form=form,
            )
        )
    elif flask.request.method == "POST":
        form = UploadForm(flask.request.form)

        if form.validate_on_submit():
            subject_id = form.subject_id.data
            data_type = form.data_type.data
            time_point = form.time_point.data
            uploaded_by = form.uploaded_by.data
            files_uploaded = form.files_uploaded.data

            files_uuid = files_uploaded.split(",") if files_uploaded else []
            files_uuid = [file_uuid for file_uuid in files_uuid if file_uuid != ""]

            submission = Submission(
                subject_id=subject_id,  # type: ignore
                data_type=data_type,  # type: ignore
                event_name=time_point,
                uploaded_by=uploaded_by,  # type: ignore
            )

            submission_id = submission.save()

            for file_uuid in files_uuid:
                submitted_files_map = SubmittedFilesMap(
                    submission_id=submission_id, file_uuid=file_uuid
                )
                submitted_files_map.save()

            flask.flash(f"Submission successful for {subject_id}", "success")
            return flask.redirect("/")  # Redirect to the home page  # type: ignore
        else:
            flask.flash("Form not submitted", "warning")
            return flask.Response(
                flask.render_template(
                    "form.html",
                    metadata=metadata,
                    title="Upload",
                    form=form,
                )
            )
    else:
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
        file_uuid = uuid.uuid4()
        file_name = werkzeug_utils.secure_filename(file.filename)  # type: ignore
        file_path = storage_path / f"{file_uuid}_{file_name}"
        with open(file_path, "wb") as f:
            file.save(f)

        uploaded_file = UploadedFile(
            uuid=str(file_uuid), file_name=file_name, file_path=file_path
        )
        uploaded_file.save()

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
        file_uuid = dz_uuid
        file_name = werkzeug_utils.secure_filename(file.filename)  # type: ignore
        file_path = storage_path / f"{file_uuid}_{file_name}"
        with open(file_path, "wb") as f:
            for file_number in range(total_chunks):
                f.write((save_dir / str(file_number)).read_bytes())
        logger.info(f"{file.filename} has been uploaded")

        uploaded_file = UploadedFile(
            uuid=str(file_uuid), file_name=file_name, file_path=file_path
        )
        uploaded_file.save()

        cli.remove_directory(save_dir)

    return flask.Response(
        status=200,
        response="Chunk uploaded successfully",
    )


@upload_bp.route("/history", methods=["GET"])
@flask_login.login_required
def history() -> flask.Response:
    """
    Returns the history of uploaded files.

    Returns:
        flask.Response: A response object.
    """
    metadata: Metadata = Metadata(flask.request)
    current_user: User = flask_login.current_user

    uploaded_files = SubmittedFilesMap.get_files_submitted_by_user(
        user_name=current_user.username
    )

    uploaded_files_list: List[UploadedFileView] = []
    for _, row in uploaded_files.iterrows():
        uploaded_file_view = UploadedFileView(
            uuid=row["uuid"],
            subject_id=row["subject_id"],
            data_type=row["data_type"],
            event_name=row["event_name"],
            file_name=row["file_name"],
            file_size_mb=row["file_size_mb"],
            uploaded_at=row["uploaded_at"],
        )
        uploaded_files_list.append(uploaded_file_view)

    return flask.Response(
        flask.render_template(
            "history.html",
            metadata=metadata,
            title="History",
            uploaded_files=uploaded_files_list,
        )
    )


@upload_bp.route("/delete/<uuid>", methods=["GET"])
@flask_login.login_required
def delete(uuid: str) -> flask.Response:
    """
    Deletes an uploaded file.

    Args:
        uuid (str): The UUID of the file.

    Returns:
        flask.Response: A response object.
    """
    uploaded_file_df: pd.DataFrame = SubmittedFilesMap.get_file_by_uuid(uuid=uuid)
    if uploaded_file_df.empty:
        flask.flash("Invalid file UUID", "error")
        return flask.redirect(flask.url_for("upload.history"))

    SubmittedFilesMap.delete(uuid=uuid)

    flask.flash("File deleted successfully", "success")
    return flask.redirect(flask.url_for("upload.history"))


@upload_bp.route("/download/<uuid>", methods=["GET"])
@flask_login.login_required
def retrieve(uuid: str) -> flask.Response:
    """
    Downloads an uploaded file.

    Args:
        uuid (str): The UUID of the file.

    Returns:
        flask.Response: A response object.
    """
    uploaded_file = UploadedFile.find_by_uuid_query(uuid=uuid)
    if not uploaded_file:
        flask.flash("Invalid file UUID", "error")
        return flask.redirect(flask.url_for("upload.history"))

    return flask.send_file(
        uploaded_file.file_path,
        as_attachment=True,
        download_name=uploaded_file.file_name,
    )
