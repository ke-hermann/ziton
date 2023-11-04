"""
Module that provides API to interact with and parse the configuration file.
"""
import logging
import pathlib

import toml

HOME_DIR = pathlib.Path.home()
CONFIG_PATH = pathlib.Path(HOME_DIR).joinpath(".ziton/config.toml")
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class InvalidConfigurationError(Exception):
    """Raised when configuration file is corrupted."""


def verify_config_integrity():
    """Verify if the configuratino file is valid and contains necessary keys."""
    LOGGER.info("Verifying integrity of the configuration file...")
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        valid = (
            "included_directories" in config
            and "index_on_startup" in config
            and "live_updates" in config
            and "hidden_files" in config
            and "database_path" in config
            and "excluded_folders" in config
            and "excluded_directories" in config
            and "min_on_launch" in config
        )
    if not valid:
        raise InvalidConfigurationError(
            "Errors found in configuration file, delete to restore default configuration."
        )


def validate_config_file():
    """Generates a basic config in case the user has not created one"""
    # create parent folder if it doesn't exist yet
    parent = CONFIG_PATH.parent
    if not parent.exists():
        parent.mkdir()

    if CONFIG_PATH.exists():
        verify_config_integrity()
        LOGGER.info(f"Loading configuration file -> '{CONFIG_PATH}'")
    else:
        # if config file wasn't found generate new basic one
        LOGGER.info("No configuration file found. Generating one for you.")
        db_path = pathlib.Path(HOME_DIR).joinpath(".ziton/database.db")
        basic_cfg = {
            "included_directories": [str(HOME_DIR)],
            "index_on_startup": False,
            "live_updates": False,
            "hidden_files": True,
            "database_path": str(db_path),
            "excluded_directories": [],
            "excluded_folders": [],
            "min_on_launch": False
        }
        with open(CONFIG_PATH, "w") as outfile:
            outfile.writelines(toml.dumps(basic_cfg))


def included_directories():
    "Get list of directories that should be indexed."
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        return config["included_directories"]


def excluded_directories():
    "Get list of directories that should be excluded."
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        return config["excluded_directories"]


def start_updated_enabled():
    "Check if startup database update is enabled."
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        return config["index_on_startup"]


def is_indexing_enabled():
    """Check if live database updates are enabled."""
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        return config["live_updates"]


def database_path():
    """Returns database path."""
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        return config["database_path"]


def save_configuration(config_dict):
    """persist current configuration settings to disk."""
    with open(CONFIG_PATH, "w") as outfile:
        toml.dump(config_dict, outfile)


def hidden_files_enabled():
    """Determine if hidden files are being indexed or not"""
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        return config["hidden_files"]


def excluded_folders():
    """folders with given filenames will not be included"""
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        return config["excluded_folders"]


def minimize_on_open():
    """if enabled ziton will minimize to tray when files or folders are opened"""
    with open(CONFIG_PATH, "r") as infile:
        config = toml.load(infile)
        return config["min_on_launch"]
