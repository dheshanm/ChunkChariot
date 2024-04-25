"""
Authenticates the user
"""

import flask
import flask_login
import werkzeug.security

from uploader.blueprints.auth.models import LoginForm, RegisterForm
from uploader.models import Metadata
from uploader.models.user import User

auth_bp = flask.Blueprint(
    "auth", __name__, url_prefix="/auth", template_folder="templates"
)


def hash_password(password: str) -> str:
    """
    Hashes a password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return werkzeug.security.generate_password_hash(password)


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> flask.Response:
    """
    Logs the user in.
    """
    if flask_login.current_user.is_authenticated:
        flask.flash("You are already logged in!", "info")
        return flask.redirect(flask.url_for("healthcheck.healthcheck"))  # type: ignore

    form = LoginForm()
    metadata = Metadata(flask.request)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data

        user = User.find_by_email_query(email=email)  # type: ignore

        if user and user.check_password(password):  # type: ignore
            # Redirect to home page
            flask.flash(f"Logged in as {user.username}", "success")
            flask_login.login_user(user, remember=remember)  # type: ignore

            # Check if there is a next page
            next_page = flask.request.args.get("next")
            if next_page:
                return flask.redirect(next_page)  # type: ignore

            return flask.redirect(flask.url_for("healthcheck.healthcheck"))  # type: ignore

        flask.flash("Invalid email or password", "error")
        return flask.redirect(flask.url_for("auth.login"))  # type: ignore

    return flask.Response(
        response=flask.render_template(
            "login.html", metadata=metadata, form=form, title="Login"
        ),
        status=200,
    )


@auth_bp.route("/logout", methods=["GET"])
def logout() -> flask.Response:
    """
    Logs the user out.
    """
    # Check if the user is logged in
    if flask_login.current_user.is_authenticated:
        flask_login.logout_user()
        flask.flash("Logged out!", "success")
    else:
        flask.flash("You are not logged in!", "error")
    return flask.redirect(flask.url_for("auth.login"))  # type: ignore


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> flask.Response:
    """
    Registers a new user.
    """
    if flask_login.current_user.is_authenticated:
        flask.flash("You are already logged in!", "info")
        return flask.redirect(flask.url_for("healthcheck.healthcheck"))  # type: ignore

    form = RegisterForm()
    metadata = Metadata(flask.request)

    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data
        password = form.password.data

        password_hash = hash_password(password)  # type: ignore

        new_user = User(username=name, email=email, password=password_hash)  # type: ignore
        new_user.save()

        # Redirect to login page
        return flask.redirect(flask.url_for("auth.login"))  # type: ignore

    return flask.Response(
        response=flask.render_template(
            "register.html", metadata=metadata, form=form, title="Register"
        ),
        status=200,
    )
