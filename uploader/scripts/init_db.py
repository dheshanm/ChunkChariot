#!/usr/bin/env python
"""
Drop all tables and recreate them.
"""

import sys
from pathlib import Path

file = Path(__file__)
parent = file.parent
ROOT = None
for parent in file.parents:
    if parent.name == "uploader":
        ROOT = parent
sys.path.append(str(ROOT))

import logging
from typing import List

from uploader.helpers import db, utils
from uploader.models.user import User

MODULE_NAME = "init_db"

logger = logging.getLogger(MODULE_NAME)
logargs = {
    "level": logging.DEBUG,
    "format": "%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s",
}
logging.basicConfig(**logargs)


def init_db(config_file: Path):
    """
    Initializes the database.

    WARNING: This will drop all tables and recreate them.
    DO NOT RUN THIS IN PRODUCTION.

    Args:
        config_file (Path): Path to the config file.
    """

    drop_queries: List[str] = [
        User.drop_table_query(),
    ]

    create_queries: List[str] = [
        User.create_table_query(),
    ]

    sql_queries: List[str] = drop_queries + create_queries

    db.execute_queries(config_file=config_file, queries=sql_queries)


if __name__ == "__main__":
    config_file = utils.get_config_file_path()

    utils.configure_logging(
        config_file=config_file, module_name=MODULE_NAME, logger=logger
    )

    logger.info(f"Using config file: {config_file}")

    logger.info("Initializing database...")
    logger.warning("This will delete all existing data in the database!")

    init_db(config_file=config_file)

    logger.info("Done!")
