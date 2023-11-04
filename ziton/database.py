"""
Sqlite Database API for the application.
Provides functionality to rebuild and interact with the database.
"""

import logging
import os
import pathlib
import sqlite3
import time
from dataclasses import dataclass

from ziton.config import (
    database_path,
    hidden_files_enabled,
    included_directories,
    excluded_folders,
    excluded_directories,
)

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


@dataclass
class DatabaseEntry:
    """dataclass container that represents a single db entry"""

    filename: str
    filepath: str
    size: int
    modified: int


def remove_database():
    """Delete DB from disk"""
    db_path = database_path()
    os.remove(db_path)
    LOGGER.info("Deleting database...")


def build_database():
    """Build database in pure python code."""
    db_path = database_path()
    check_hidden = hidden_files_enabled()
    # establish connection and create table if it doesn'T exist yet
    LOGGER.info("Complete database rebuild...(python backend)")
    start_time = time.time()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS files(filename TEXT, filepath TEXT,
            size INT, modified INT);"""
    )
    cursor.execute("""DELETE FROM files;""")
    # iterate over disk and build file entries
    directories = included_directories()
    ex_folders = excluded_folders()
    ex_dirs = excluded_directories()
    file_list = []
    for directory in directories:
        for root, dirs, files in os.walk(directory, topdown=True):
            if not check_hidden:
                files = [f for f in files if not f[0] == "."]
                dirs[:] = [
                    d
                    for d in dirs
                    if not d[0] == "."
                    and d not in ex_folders
                    and os.path.join(root, d) not in ex_dirs
                ]
            # iterate over files and directories
            for fil in files:
                path = os.path.join(root, fil)
                if os.path.exists(path):
                    f_info = os.stat(path)
                    size = int(f_info.st_size)
                    modified = int(f_info.st_mtime)
                    file_list.append((fil, path, size, modified))
            for d in dirs:
                path = os.path.join(root, d)
                if path in ex_dirs:
                    print(path)
                    continue
                if os.path.exists(path):
                    file_list.append((d, path, 0, 0))
    # # write file entries to database
    cursor.executemany("INSERT INTO files VALUES (?, ?, ?, ?)", file_list)
    conn.commit()
    conn.close()

    t_end = time.time() - start_time
    LOGGER.info(f"Full rebuild finished. Time elapsed: {t_end:.2f}s")


def number_of_rows():
    "Number of entries in the table."

    conn = sqlite3.connect(database_path())
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM files")
    data = cursor.fetchall()
    conn.close()
    return data[0][0]


def validate_database():
    "Check if database exists, if not build it."
    LOGGER.info(f"Validating Database ... -> '{database_path()}' ")
    path = pathlib.Path(database_path())
    if not path.parent.exists():
        pathlib.Path(database_path()).parent.mkdir()
    if not path.exists():
        build_database()
        return
    # verify database health
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    status = cursor.fetchall()[0][0]
    conn.commit()
    conn.close()
    # if db is in a bad state remove and rebuild
    if status != "ok":
        os.remove(path)
        build_database()


def dbrecord_from_path(filepath):
    "Builds up a dataclass that represents a db record for the `files` table."
    fileinfo = os.stat(filepath)
    filename = str(pathlib.Path(filepath).name)
    filesize = fileinfo.st_size
    modified = fileinfo.st_mtime
    db_record = DatabaseEntry(filename, filepath, filesize, modified)
    return db_record
