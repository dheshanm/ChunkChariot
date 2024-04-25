"""
Models for the uploader application.
"""

from typing import Optional

import flask

from uploader.models.user import User
from uploader import constants


class Metadata:
    """
    Metadata class to store request metadata.
    """

    def __init__(self, request_obj: flask.Request, current_user: Optional[User] = None):
        self.request = request_obj
        self.current_user = current_user
        self.app_name = constants.APP_NAME
