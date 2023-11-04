"""
Central entry point for the application.
"""

import sys
from pathlib import Path

from PySide2.QtCore import QCoreApplication, Qt, Signal, Slot
from PySide2.QtGui import QIcon
from PySide2.QtSql import QSqlDatabase, QSqlQuery
from PySide2.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget

import ziton.database as db
import ziton.icons as icons
import ziton.monitor as monitor
from ziton.config import database_path, is_indexing_enabled
from ziton.widgets.entries_trayicon import TrayEntryInfo
from ziton.widgets.menubar import Menubar
from ziton.widgets.systemtray import Systemtray
from ziton.widgets.tableview import Tableview

STYLESHEET = Path(__name__).resolve().parent.joinpath("ziton/resources/stylesheet.qss")


class Mainwindow(QWidget):
    """Central widget and entrypoint for the program."""

    selChanged = Signal(str)

    def __init__(self):
        """Initialises main window"""
        QWidget.__init__(self)
        # connect to existing DB
        self.database = QSqlDatabase.addDatabase("QSQLITE")
        self.database.setDatabaseName(database_path())
        self.database.open()
        self.file_monitor = monitor.FileMonitor()
        # start monitoring the filesystem for changes
        if is_indexing_enabled():
            self.file_monitor.worker.start()

        # widgets
        self.searchbar = QLineEdit()
        self.searchbar.setClearButtonEnabled(True)
        self.menubar = Menubar(self.file_monitor.worker)
        self.trayinfo = TrayEntryInfo()
        self.view = Tableview()

        # set layout
        self.central_layout = QVBoxLayout()
        self.central_layout.addWidget(self.menubar)
        self.central_layout.addWidget(self.searchbar)
        self.central_layout.addWidget(self.view)
        self.central_layout.addWidget(self.trayinfo)
        self.setLayout(self.central_layout)

        # signals
        self.searchbar.textChanged.connect(self.view.update_filter)
        self.view.selectionModel().selectionChanged.connect(self.update_tray)
        self.view.tabPressed.connect(self.focus_searchbar)
        self.selChanged.connect(self.trayinfo.update_selected_text)
        self.menubar.dbUpdated.connect(self.trayinfo.start_loading_animation)
        self.menubar.dbUpdated.connect(self.trayinfo.update_filecount)
        self.menubar.worker_finished.connect(self.trayinfo.stop_loading_animation)
        if is_indexing_enabled():
            self.file_monitor.fileAdded.connect(self.file_created)
            self.file_monitor.fileDeleted.connect(self.file_deleted)

    def closeEvent(self, event):
        """overriding window close to quit threads gracefully"""
        self.file_monitor.worker.terminate()
        self.file_monitor.worker.wait()
        QCoreApplication.quit()

    def update_tray(self, item):
        """Update the tray information when selection has changed."""
        indexes = item.indexes()
        # get first column that contains the file's name and update the tray
        name = self.view.model().data(indexes[0])
        self.selChanged.emit(name)

    @Slot()
    def focus_searchbar(self):
        """puts searchbar into focus."""
        self.searchbar.setFocus()

    @Slot()
    def file_created(self, filepath):
        """Consume inotify file creation event."""
        if Path(filepath).exists():
            new_db_entry = db.dbrecord_from_path(filepath)
            query = QSqlQuery()
            query.prepare("INSERT INTO files VALUES (?, ?, ?, ?)")
            query.bindValue(0, new_db_entry.filename)
            query.bindValue(1, new_db_entry.filepath)
            query.bindValue(2, new_db_entry.size)
            query.bindValue(3, new_db_entry.modified)
            query.exec_()
            self.trayinfo.update_filecount()

    @Slot()
    def file_deleted(self, filepath):
        """consume inotify file deletion event."""
        query = QSqlQuery()
        query.prepare("DELETE FROM files WHERE filepath=?")
        query.bindValue(0, filepath)
        query.exec_()
        self.trayinfo.update_filecount()

    @Slot(str)
    def toggle_visual_state(self):
        """Toggles minimizing or normalising the window"""
        if self.isMinimized():
            self.showNormal()
            self.activateWindow()
        else:
            self.showMinimized()


def main():
    """program entrypoint."""
    with open(STYLESHEET, "r") as infile:
        stylesheet = infile.read()

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app_icon = QIcon(str(icons.LOGO))
    app.setStyleSheet(stylesheet)
    app.setWindowIcon(app_icon)
    app.setApplicationDisplayName("Ziton")

    mainwindow = Mainwindow()
    mainwindow.resize(1200, 800)
    systray = Systemtray(app)
    systray.activated.connect(mainwindow.toggle_visual_state)

    mainwindow.show()
    systray.show()

    sys.exit(app.exec_())
