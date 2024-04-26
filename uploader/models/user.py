"""
User model.
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

import flask_login
import werkzeug.security

from uploader.helpers import db, utils

logger = logging.getLogger(__name__)


class User(flask_login.UserMixin):
    """
    User model.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password of the user.
    """

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        created_at: Optional[datetime] = None,
    ):
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at

    def __repr__(self):
        return f"<User {self.email}>"

    def __str__(self):
        return self.__repr__()

    def get_id(self):
        return self.email

    def check_password(self, password: str) -> bool:
        """
        Checks if the given password matches the user's password.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches, otherwise False.
        """
        logger.debug(f"Checking password for {self.email}")
        logger.debug(f"Password: {self.password}")
        logger.debug(f"Given password: {password}")
        return werkzeug.security.check_password_hash(
            pwhash=self.password, password=password
        )

    @staticmethod
    def create_table_query() -> str:
        """
        Returns the query to create the users table.

        Returns:
            str: The query to create the users table.
        """
        sql_query = """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT NOT NULL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        return sql_query

    @staticmethod
    def drop_table_query() -> str:
        """
        Returns the query to drop the users table.

        Returns:
            str: The query to drop the users table.
        """
        sql_query = """
        DROP TABLE IF EXISTS users
        """

        return sql_query

    def insert_query(self) -> str:
        """
        Returns the query to insert the user into the users table.

        Returns:
            str: The query to insert the user into the users table.
        """

        sanitized_email = self.email.strip().lower()

        sql_query = f"""
        INSERT INTO users (username, email, password_hash)
        VALUES ('{self.username}', '{sanitized_email}', '{self.password}')
        """

        return sql_query

    def save(self, config_file: Optional[Path] = None) -> None:
        """
        Saves the user to the database.

        Args:
            config_file (Path): The path to the database configuration file.
        """
        if config_file is None:
            config_file = utils.get_config_file_path()

        db.execute_queries(config_file=config_file, queries=[self.insert_query()])

        logger.debug(f"User {self.email} saved to the database.")
        return None

    @staticmethod
    def find_by_username_query(
        username: str, config_file: Optional[Path] = None
    ) -> "Optional[User]":
        """
        Returns the query to find a user by username.

        Args:
            username (str): The username of the user to find.
            config_file (Path): The path to the database configuration file.

        Returns:
            str: The query to find a user by username.
        """
        if config_file is None:
            config_file = utils.get_config_file_path()

        sql_query = f"""
        SELECT * FROM users WHERE username = '{username}'
        """

        df = db.execute_sql(config_file=config_file, query=sql_query)

        if df.empty:
            return None

        user = User(
            username=df.iloc[0]["username"],
            email=df.iloc[0]["email"],
            password=df.iloc[0]["password_hash"],
            created_at=df.iloc[0]["created_at"],
        )

        return user

    @staticmethod
    def find_by_email_query(
        email: str, config_file: Optional[Path] = None
    ) -> "Optional[User]":
        """
        Returns User object if the user is found by email.

        Args:
            email (str): The email of the user to find.
            config_file (Path): The path to the database configuration file.

        Returns:
            Optional[User]: The user object if found, otherwise None.
        """
        if config_file is None:
            config_file = utils.get_config_file_path()

        sql_query = f"""
        SELECT *
        FROM users
        WHERE email = '{email}'
            AND is_active = TRUE
        """

        df = db.execute_sql(config_file=config_file, query=sql_query)

        if df.empty:
            return None

        user = User(
            username=df.iloc[0]["username"],
            email=df.iloc[0]["email"],
            password=df.iloc[0]["password_hash"],
            created_at=df.iloc[0]["created_at"],
        )

        return user
