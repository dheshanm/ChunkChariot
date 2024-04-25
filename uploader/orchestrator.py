"""
Module to orchestrate the app.
"""

from pathlib import Path

from uploader.helpers.config import config


def get_secret_key(config_file: Path) -> str:
    """
    Returns the secret key for the app from the config file.

    Args:
        config_file (Path): The path to the config file.

    Returns:
        str: The secret key for the app.
    """
    config_params = config(path=config_file, section="flask")
    secret_key = config_params["secret_key"]

    return secret_key


def get_storage_path(config_file: Path) -> Path:
    """
    Returns the path to store uploaded files.

    Args:
        config_file (Path): The path to the config file.

    Returns:
        Path: The path to store uploaded files.
    """
    config_params = config(path=config_file, section="upload")
    storage_path = Path(config_params["storage_path"])

    if not storage_path.exists():
        storage_path.mkdir(parents=True)

    return storage_path


def get_chunk_path(config_file: Path) -> Path:
    """
    Returns the path to store uploaded chunks.

    Args:
        config_file (Path): The path to the config file.

    Returns:
        Path: The path to store uploaded chunks.
    """

    config_params = config(path=config_file, section="upload")
    chunk_path = Path(config_params["chunk_path"])

    if not chunk_path.exists():
        chunk_path.mkdir(parents=True)

    return chunk_path
