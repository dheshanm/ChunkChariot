"""
Model to map submitted files to submissions
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from uploader.helpers import db, utils
from uploader.models.uploaded_file import UploadedFile


class SubmittedFilesMap:
    """
    Submitted files map model.

    Attributes:
        submission_id (int): The ID of the submission.
        file_uuid (str): The UUID of the file.
    """

    def __init__(self, submission_id: int, file_uuid: str) -> None:
        self.submission_id = submission_id
        self.file_uuid = file_uuid

    def __repr__(self) -> str:
        return f"<SubmittedFilesMap {self.submission_id} {self.file_uuid}>"

    def __str__(self) -> str:
        return self.__repr__()

    @staticmethod
    def create_table_query() -> str:
        """
        Returns the SQL query to create the submitted_files_map table.

        Returns:
            str: The SQL query.
        """

        sql_query = """
        CREATE TABLE IF NOT EXISTS submitted_files_map (
            submission_id INTEGER NOT NULL REFERENCES submissions(id),
            file_uuid TEXT NOT NULL REFERENCES uploaded_files(uuid),
            PRIMARY KEY (submission_id, file_uuid)
        )
        """

        return sql_query

    @staticmethod
    def drop_table_query() -> str:
        """
        Returns the SQL query to drop the submitted_files_map table.

        Returns:
            str: The SQL query.
        """

        sql_query = """
        DROP TABLE IF EXISTS submitted_files_map
        """

        return sql_query

    def insert_query(self) -> str:
        """
        Returns the SQL query to insert the submitted files map into the submitted_files_map table.

        Returns:
            str: The SQL query.
        """

        sql_query = f"""
        INSERT INTO submitted_files_map (submission_id, file_uuid)
        VALUES ({self.submission_id}, '{self.file_uuid}')
        """

        return sql_query

    def save(self, config_file: Optional[Path] = None) -> None:
        """
        Saves the submitted files map to the database.

        Args:
            config_file (Optional[Path]): The path to the config file.
        """
        if not config_file:
            config_file = utils.get_config_file_path()

        db.execute_queries(config_file=config_file, queries=[self.insert_query()])

        return None

    @staticmethod
    def get_files_submitted_by_user(
        user_name: str, config_file: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Returns the files submitted by a user.

        Args:
            user_name (str): The name of the user.
            config_file (Optional[Path]): The path to the config file.

        Returns:
            pd.DataFrame: The files submitted by the user.
        """
        if not config_file:
            config_file = utils.get_config_file_path()

        query = f"""
        SELECT submissions.*, uploaded_files.*
        FROM submitted_files_map
        LEFT JOIN submissions ON submissions.id = submitted_files_map.submission_id
        LEFT JOIN uploaded_files ON uploaded_files."uuid" = submitted_files_map.file_uuid
        WHERE submissions.uploaded_by = '{user_name}'
        ORDER BY uploaded_files.uploaded_at DESC;
        """

        df = db.execute_sql(config_file=config_file, query=query)

        return df

    @staticmethod
    def get_file_by_uuid(uuid: str, config_file: Optional[Path] = None) -> pd.DataFrame:
        """
        Returns the file by UUID.

        Args:
            uuid (str): The UUID of the file.
            config_file (Optional[Path]): The path to the config file.

        Returns:
            pd.DataFrame: The file.
        """
        if not config_file:
            config_file = utils.get_config_file_path()

        query = f"""
        SELECT submissions.*, uploaded_files.*
        FROM submitted_files_map
        LEFT JOIN submissions ON submissions.id = submitted_files_map.submission_id
        LEFT JOIN uploaded_files ON uploaded_files."uuid" = submitted_files_map.file_uuid
        WHERE uploaded_files.uuid = '{uuid}';
        """

        df = db.execute_sql(config_file=config_file, query=query)

        return df

    @staticmethod
    def delete(uuid: str, config_file: Optional[Path] = None) -> None:
        """
        Deletes the file by UUID.

        Args:
            uuid (str): The UUID of the file.
            config_file (Optional[Path]): The path to the config file.
        """
        if not config_file:
            config_file = utils.get_config_file_path()

        # Delete the file from disk
        UploadedFile.delete_file(uuid=uuid)

        delete_queries = []

        delete_submitted_files_map_query = f"""
        DELETE FROM submitted_files_map
        WHERE file_uuid = '{uuid}';
        """

        delete_uploaded_files_query = f"""
        DELETE FROM uploaded_files
        WHERE uuid = '{uuid}';
        """

        delete_queries.append(delete_submitted_files_map_query)
        delete_queries.append(delete_uploaded_files_query)

        db.execute_queries(config_file=config_file, queries=delete_queries)

        return None
