"""
Widget that represents the preferences submenu.
"""

import subprocess
import shutil
from pathlib import Path

from PySide2.QtCore import QFile, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import (
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFileDialog,
)

import ziton.config as cfg

FILE_PATH = Path(__name__).resolve().parent
PREFERENCES = FILE_PATH.joinpath("ziton/resources/ui/preferences.ui")


class PreferenceDialog:
    """Represents the settings dialog."""

    def __init__(self):
        """inits the settingsd dialog."""
        # load ui file
        ui_file = QFile(str(PREFERENCES))
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        # widgets
        self.add_item_btn = self.window.findChild(QPushButton, "add_item")
        self.remove_item_btn = self.window.findChild(QPushButton, "remove_item")
        self.directory_list = self.window.findChild(QListWidget, "included_files")
        self.update_startup_box = self.window.findChild(QCheckBox, "update_startup_box")
        self.live_indexing_box = self.window.findChild(QCheckBox, "live_indexing_box")
        self.hidden_indexing_box = self.window.findChild(
            QCheckBox, "hidden_indexing_box"
        )
        self.save_btn = self.window.findChild(QPushButton, "save_btn")
        self.close_btn = self.window.findChild(QPushButton, "close_btn")
        self.config_btn = self.window.findChild(QPushButton, "config_btn")
        self.min_on_launch_btn = self.window.findChild(QCheckBox, "min_on_launch")
        # signals
        self.add_item_btn.clicked.connect(self.insert_row)
        self.remove_item_btn.clicked.connect(self.remove_selected)
        self.config_btn.clicked.connect(self.open_config_file)
        self.save_btn.clicked.connect(self.save_configuration)
        self.close_btn.clicked.connect(self.window.accept)
        # load existing config
        for directory in cfg.included_directories():
            self.insert_row(directory)
        self.update_startup_box.setChecked(cfg.start_updated_enabled())
        self.live_indexing_box.setChecked(cfg.is_indexing_enabled())
        self.hidden_indexing_box.setChecked(cfg.hidden_files_enabled())

        self.window.exec_()

    def open_file_dialog(self):
        """open file browser and select file"""
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        if dlg.exec_():
            sel_file = dlg.selectedFiles()[0]
            return sel_file

    def insert_row(self, path=None):
        """Insert a new row."""
        if not path:
            path = self.open_file_dialog()
        new_item = QListWidgetItem()
        new_item.setText(path)
        new_item.setFlags(new_item.flags() | Qt.ItemIsEditable)
        i = self.directory_list.count()
        self.directory_list.insertItem(i, new_item)

    def remove_selected(self):
        """Removes a row."""
        selected = self.directory_list.selectedItems()
        for sel in selected:
            self.directory_list.takeItem(self.directory_list.row(sel))

    def save_configuration(self):
        """writes configuraton changes to disk."""
        dirs = [
            self.directory_list.item(i).text()
            for i in range(self.directory_list.count())
        ]
        current_config = {
            "included_directories": dirs,
            "index_on_startup": self.update_startup_box.isChecked(),
            "live_updates": self.live_indexing_box.isChecked(),
            "hidden_files": self.hidden_indexing_box.isChecked(),
            "database_path": cfg.database_path(),
            "excluded_folders": cfg.excluded_folders(),
            "excluded_directories": cfg.excluded_directories(),
            "min_on_launch": self.min_on_launch_btn.isChecked()
        }
        cfg.save_configuration(current_config)
        # close the dialog
        self.window.accept()

    def open_config_file(self):
        """Open the configuration file."""
        p = cfg.CONFIG_PATH
        if shutil.which("dolphin"):
            subprocess.run(["dolphin", p], check=False)
        else:
            subprocess.run(["xdg-open", p], check=False)
