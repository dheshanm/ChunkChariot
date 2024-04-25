"""
Module providing command line interface for the app.
"""

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def get_repo_root() -> str:
    """
    Returns the root directory of the current Git repository.

    Uses the command `git rev-parse --show-toplevel` to get the root directory.
    """
    repo_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
    repo_root = repo_root.decode("utf-8").strip()

    logger.debug(f"Repo root: {repo_root}")

    return repo_root


def remove_directory(directory: Path) -> None:
    """
    Removes a directory.

    Args:
        directory (str): The directory to remove.
    """
    logger.debug(f"Removing directory: {directory}")
    shutil.rmtree(directory)
