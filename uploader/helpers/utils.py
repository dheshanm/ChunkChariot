"""
Utility functions for the uploader.
"""

import logging
from pathlib import Path
from datetime import datetime

from uploader.helpers import cli
from uploader.helpers.config import config


def get_config_file_path() -> Path:
    """
    Returns the path to the config file.

    Returns:
        str: The path to the config file.

    Raises:
        ConfigFileNotFoundExeption: If the config file is not found.
    """
    repo_root = cli.get_repo_root()
    config_file_path = repo_root + "/config.ini"

    # Check if config_file_path exists
    if not Path(config_file_path).is_file():
        raise FileNotFoundError(f"Config file not found at {config_file_path}")

    return Path(config_file_path)


def configure_logging(config_file: Path, module_name: str, logger: logging.Logger):
    """
    Configures logging for a given module using the specified configuration file.

    Rotates the log file if it exceeds 10MB.

    Args:
        config_file (str): The path to the configuration file.
        module_name (str): The name of the module to configure logging for.
        logger (logging.Logger): The logger object to use for logging.

    Returns:
        None
    """
    log_params = config(config_file, "logging")
    log_file = Path(log_params[module_name])

    if not log_file.is_absolute():
        log_file = Path(cli.get_repo_root()) / log_file
        log_file.parent.mkdir(parents=True, exist_ok=True)

    if log_file.exists() and log_file.stat().st_size > 10000000:  # 10MB
        archive_file = (
            log_file.parent
            / "archive"
            / f"{log_file.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        )
        logger.info(f"Rotating log file to {archive_file}")

        archive_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.rename(archive_file)

    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s  - %(process)d - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]"
        )
    )

    logging.getLogger().addHandler(file_handler)
    logger.info(f"Logging to {log_file}")
