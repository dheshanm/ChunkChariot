"""
Contains the models for the authentication app.
"""

import logging

import wtforms
from flask_wtf import FlaskForm

from uploader.models.user import User

logger = logging.getLogger(__name__)


class RegisterForm(FlaskForm):
    """
    Register form class.
    """

    email = wtforms.StringField(
        "Email",
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()],
        description="Please use your official email address",
    )
    username = wtforms.StringField(
        "REDCap Username",
        validators=[wtforms.validators.DataRequired()],
        description="Enter your REDCap username",
    )
    password = wtforms.PasswordField(
        "Password", validators=[wtforms.validators.DataRequired()]
    )
    confirm_password = wtforms.PasswordField(
        "Confirm Password",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.EqualTo("password", message="Passwords must match"),
        ],
    )

    submit = wtforms.SubmitField("Register")

    def validate_email(self, email: wtforms.StringField) -> None:
        """
        Validate email address.
        """
        user = User.find_by_email_query(email=email.data)  # type: ignore
        if user:
            logger.info(f"Email already in use: {email.data}")
            raise wtforms.validators.ValidationError("Email already in use")

        return None

    def validate_username(self, username: wtforms.StringField) -> None:
        """
        Validate REDCap username.
        """
        user = User.find_by_username_query(username=username.data)  # type: ignore
        if user:
            logger.info(f"Username already in use: {username.data}")
            raise wtforms.validators.ValidationError(
                "Username already in use. If you already have an account, please login instead."
            )

        return None


class LoginForm(FlaskForm):
    """
    Login form class.
    """

    email = wtforms.StringField(
        "Email",
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()],
    )
    password = wtforms.PasswordField(
        "Password", validators=[wtforms.validators.DataRequired()]
    )
    remember = wtforms.BooleanField("Remember Me", default=False)

    submit = wtforms.SubmitField("Login")
