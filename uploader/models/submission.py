"""
Submission model
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from uploader.helpers import db, utils


class Submission:
    """
    Submission model.

    Attributes:
        subject_id (str): The subject id associated with the submission.
        data_type (str): The data type of the uploaded file(s).
        event_name (str): The name of the REDCap event associated with the submission.
        uploaded_by (str): The username of the user who made the submission.
        submission_timestamp (datetime): The time at which the submission was made.
    """

    def __init__(
        self, subject_id: str, data_type: str, event_name: str, uploaded_by: str
    ):
        self.id = None
        self.subject_id = subject_id
        self.data_type = data_type
        self.event_name = event_name
        self.uploaded_by = uploaded_by
        self.submission_timestamp = datetime.now()

    def __repr__(self):
        return f"<Submission {self.subject_id}>"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def create_table_query() -> str:
        """
        Returns the SQL query to create the submissions table.

        Returns:
            str: The SQL query.
        """

        sql_query = """
        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,
            subject_id TEXT,
            data_type TEXT NOT NULL,
            event_name TEXT NOT NULL,
            uploaded_by TEXT NOT NULL REFERENCES users(username),
            submission_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """

        return sql_query

    @staticmethod
    def drop_table_query() -> str:
        """
        Returns the SQL query to drop the submissions table.

        Returns:
            str: The SQL query.
        """
        sql_query = "DROP TABLE IF EXISTS submissions"

        return sql_query

    def insert_query(self) -> str:
        """
        Returns the SQL query to insert the submission into the submissions table.

        Returns:
            str: The SQL query.
        """

        sql_query = f"""
        INSERT INTO submissions (subject_id, data_type, event_name, uploaded_by)
        VALUES ('{self.subject_id}', '{self.data_type}', '{self.event_name}', '{self.uploaded_by}')
        RETURNING id
        """

        return sql_query

    def save(self, config_file: Optional[Path] = None) -> int:
        """
        Saves the submission to the database.

        Args:
            config_file (Path): Path to the config file.

        Returns:
            int: The ID of the inserted row.
        """
        if not config_file:
            config_file = utils.get_config_file_path()

        inserted_id = db.execute_insert_query(
            config_file=config_file, query=self.insert_query()
        )
        self.id = int(inserted_id)

        return self.id

    @staticmethod
    def get_submission_by_id(
        submission_id: int, config_file: Optional[Path] = None
    ) -> Optional["Submission"]:
        """
        Retrieves a submission by its ID.

        Args:
            submission_id (int): The ID of the submission.
            config_file (Path): Path to the config file.

        Returns:
            Optional[Submission]: The submission object or None if not found.
        """
        if not config_file:
            config_file = utils.get_config_file_path()

        query = f"SELECT * FROM submissions WHERE id = {submission_id}"
        result_df = db.execute_sql(config_file=config_file, query=query)

        if result_df.empty:
            return None

        submission = Submission(
            subject_id=result_df["subject_id"].values[0],
            data_type=result_df["data_type"].values[0],
            event_name=result_df["event_name"].values[0],
            uploaded_by=result_df["uploaded_by"].values[0],
        )

        submission.id = submission_id

        return submission

    @staticmethod
    def get_submissions_by_user(
        username: str, config_file: Optional[Path] = None
    ) -> List["Submission"]:
        """
        Retrieves all submissions made by a user.

        Args:
            username (str): The username of the user.
            config_file (Path): Path to the config file.

        Returns:
            Optional[Submission]: The submission object or None if not found.
        """
        if not config_file:
            config_file = utils.get_config_file_path()

        query = f"SELECT * FROM submissions WHERE uploaded_by = '{username}'"
        result_df = db.execute_sql(config_file=config_file, query=query)

        if result_df.empty:
            return []

        submissions: List[Submission] = []
        for _, row in result_df.iterrows():
            submission = Submission(
                subject_id=row["subject_id"],
                data_type=row["data_type"],
                event_name=row["event_name"],
                uploaded_by=row["uploaded_by"],
            )

            submission.id = row["id"]
            submissions.append(submission)

        return submissions
