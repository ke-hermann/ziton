"""
Rightclick contextmenu for the tableview.
"""
import logging
import os
import subprocess
import shutil
from pathlib import PurePath

import ziton.database as db
import ziton.icons as icons
from PySide2.QtGui import QIcon
from PySide2.QtSql import QSqlQuery
from PySide2.QtWidgets import QAction, QMenu

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class RightClickMenu(QMenu):
    """Represents the tableview's context menu."""

    def __init__(self, filepath, position):
        QMenu.__init__(self)
        self.filepath = filepath
        self.position = position
        # open parent folder of file
        self.open_action = QAction(QIcon(str(icons.FOLDER)), "Open Folder")
        self.open_action.triggered.connect(self.open_selected_folder)
        # delete selected file
        self.delete_action = QAction(QIcon(str(icons.TRASH)), "Delete File")
        self.delete_action.triggered.connect(self.delete_file)
        self.addAction(self.open_action)
        self.addAction(self.delete_action)

    def open_selected_folder(self):
        """Open folder of currently selected file."""
        parent_dir = PurePath(self.filepath).parent
        if shutil.which("dolphin"):
            subprocess.run(["dolphin", parent_dir], check=False)
        else:
            subprocess.run(["xdg-open", parent_dir], check=False)

    def remove_record(self):
        "remove record from the table."
        LOGGER.info("deleting row from table...")
        query = QSqlQuery()
        query.prepare("DELETE FROM files WHERE filepath=?")
        query.bindValue(0, self.filepath)
        query.exec_()

    def delete_file(self):
        """Deletes a file from disk."""
        os.remove(self.filepath)
        self.remove_record()
        LOGGER.info(f"deleting {self.filepath}...")
