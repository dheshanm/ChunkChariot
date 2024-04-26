"""
Model to map submitted files to submissions
"""

from pathlib import Path
from typing import Optional

from uploader.helpers import db, utils


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
