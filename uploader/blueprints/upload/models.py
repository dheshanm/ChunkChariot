"""
Contains the models for the upload blueprint.
"""

import logging

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
