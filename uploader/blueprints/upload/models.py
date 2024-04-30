"""
Contains the models for the upload blueprint.
"""

import logging
from dataclasses import dataclass

import wtforms
from flask_wtf import FlaskForm

logger = logging.getLogger(__name__)


class UploadForm(FlaskForm):
    """
    Upload form class.
    """

    subject_id = wtforms.StringField(
        "Subject ID",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(
                min=7, max=7, message="Subject ID must be 7 characters"
            ),
        ],
        description="Enter the subject ID",
    )
    data_type = wtforms.SelectField(
        "Data Type",
        choices=[
            ("eeg", "EEG"),
            ("mri", "MRI"),
            ("video", "Video"),
            ("other", "Other"),
        ],
        validators=[wtforms.validators.DataRequired()],
        description="Select the type of data you are uploading",
    )

    time_point = wtforms.SelectField(
        "Event Name",
        choices=[
            ("baseline", "Baseline"),
            ("Month 1", "Month 1"),
            ("Month 3", "Month 3"),
            ("Month 6", "Month 6"),
            ("Month 12", "Month 12"),
            ("Month 24", "Month 24"),
            ("Other", "Other"),
        ],
        validators=[wtforms.validators.DataRequired()],
        description="Select the event name (Must match REDCap event name)",
    )

    uploaded_by = wtforms.StringField(
        "Uploaded By",
        validators=[wtforms.validators.DataRequired()],
        description="Uses your REDCap ID",
    )

    # date_uploaded = wtforms.HiddenField(
    #     "Date Uploaded",
    #     validators=[wtforms.validators.DataRequired()],
    # )

    files_uploaded = wtforms.HiddenField(
        "Files Uploaded",
    )


@dataclass
class UploadedFileView:
    """
    Uploaded file dataclass.

    Attributes:
        uuid (str): The UUID of the file.
        subject_id (str): The subject ID of the file.
        data_type (str): The data type of the file.
        event_name (str): The event name of the file.
        file_name (str): The name of the file.
        file_size_mb (int): The size of the file in MB.
        uploaded_at (str): The date and time the file was uploaded.
    """

    #  {
    #     "subject_id": row["subject_id"],
    #     "data_type": row["data_type"],
    #     "event_name": row["event_name"],
    #     "file_name": row["file_name"],
    #     "file_size": row["file_size_mb"],
    #     "uploaded_at": row["uploaded_at"]
    # }

    uuid: str
    subject_id: str
    data_type: str
    event_name: str
    file_name: str
    file_size_mb: int
    uploaded_at: str

    def __repr__(self) -> str:
        return f"<UploadedFile {self.subject_id} {self.data_type} {self.event_name}>"
