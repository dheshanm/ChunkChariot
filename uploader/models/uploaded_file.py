"""
UploadedFile model
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from uploader.helpers import db, utils

logger = logging.getLogger(__name__)


class UploadedFile:
    """
    UploadedFile model.

    Attributes:
        file_path (Path): The path to the uploaded file.
        file_name (str): The name of the uploaded file.
        file_size (int): The size of the uploaded file.
        uploaded_at (datetime): The time at which the file was uploaded.
    """

    def __init__(self, uuid: str, file_name: str, file_path: Path):
        self.uuid = uuid
        self.file_name = file_name
        self.file_path = file_path
        self.file_size_mb = round(file_path.stat().st_size / (1024 * 1024), 2)
        created_time = file_path.stat().st_ctime
        self.uploaded_at = datetime.fromtimestamp(created_time)

    def __repr__(self):
        return f"<UploadedFile {self.file_name}>"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def create_table_query() -> str:
        """
        Returns the SQL query to create the uploaded_files table.

        Returns:
            str: The SQL query.
        """

        sql_query = """
        CREATE TABLE IF NOT EXISTS uploaded_files (
            uuid TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size_mb REAL NOT NULL,
            uploaded_at TIMESTAMP NOT NULL
        )
        """

        return sql_query

    @staticmethod
    def drop_table_query() -> str:
        """
        Returns the SQL query to drop the uploaded_files table.

        Returns:
            str: The SQL query.
        """
        sql_query = "DROP TABLE IF EXISTS uploaded_files"

        return sql_query

    def insert_query(self) -> str:
        """
        Returns the SQL query to insert the uploaded file into the database.

        Returns:
            str: The SQL query.
        """
        sql_query = f"""
        INSERT INTO uploaded_files (
            uuid, file_name, file_path,
            file_size_mb, uploaded_at
        )
        VALUES (
            '{self.uuid}', '{self.file_name}', '{self.file_path}',
            {self.file_size_mb}, '{self.uploaded_at}'
        )
        """

        return sql_query

    def save(self, config_file: Optional[Path] = None) -> None:
        """
        Saves the uploaded file to the database.

        Args:
            config_file (Path): The path to the database configuration file.
        """
        if not config_file:
            config_file = utils.get_config_file_path()

        db.execute_queries(config_file=config_file, queries=[self.insert_query()])

        return None

    @staticmethod
    def find_by_uuid_query(
        uuid: str, config_file: Optional[Path] = None
    ) -> "Optional[UploadedFile]":
        """
        Returns the UploadedFile with the given UUID.

        Args:
            uuid (str): The UUID of the uploaded file.
            config_file (Path): The path to the database configuration file.

        Returns:
            Optional[UploadedFile]: The UploadedFile with the given UUID.
        """
        if config_file is None:
            config_file = utils.get_config_file_path()

        sql_query = f"SELECT * FROM uploaded_files WHERE uuid = '{uuid}'"

        df = db.execute_sql(config_file=config_file, query=sql_query)

        if df.empty:
            return None

        uploaded_file = UploadedFile(
            uuid=df.iloc[0]["uuid"],
            file_name=df.iloc[0]["file_name"],
            file_path=Path(df.iloc[0]["file_path"]),
        )

        uploaded_file.file_size_mb = df.iloc[0]["file_size_mb"]
        uploaded_file.uploaded_at = datetime.fromisoformat(str(df.iloc[0]["uploaded_at"]))

        return uploaded_file

    @staticmethod
    def delete_file(uuid: str, config_file: Optional[Path] = None) -> None:
        """
        Deletes the uploaded file with the given UUID from disk.

        Use SubmittedFilesMap.delete to delete the file from the database.

        Args:
            uuid (str): The UUID of the uploaded file.
            config_file (Path): The path to the database configuration file.
        """
        if config_file is None:
            config_file = utils.get_config_file_path()

        uploaded_file = UploadedFile.find_by_uuid_query(
            uuid=uuid, config_file=config_file
        )

        if uploaded_file is not None:
            logger.info(f"Deleting file {uploaded_file.file_path}")
            uploaded_file.file_path.unlink()

        return None
