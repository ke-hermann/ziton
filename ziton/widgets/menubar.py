"""
Widget that represents the menubar.
"""
import logging
import pathlib

import ziton.database as db
import ziton.icons as icons
from PySide2.QtCore import QCoreApplication, QThread, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMenu, QSizePolicy, QToolBar, QWidget
from ziton.config import database_path
from ziton.widgets.icon_provider import IconProvider
from ziton.widgets.preferences import PreferenceDialog

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class Worker(QThread):
    """Qt Worker Thread, responsible for handling one inotify thread."""

    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            path = pathlib.PosixPath(database_path())
            db.build_database()
            self.parent().update_finished()
            LOGGER.info("db update finished!")
            self.finished.emit()
        except Exception as e:
            LOGGER.error(f"Error: {e}, trying again...")
            db.remove_database()
            db.build_database()
            self.finished.emit()


class Menubar(QToolBar):
    """Menubar widget."""

    dbUpdated = Signal(str)
    worker_finished = Signal()

    def __init__(self, worker):
        """Initialises the menu bar."""
        self.file_worker = worker
        # data
        self.icon_provider = IconProvider()
        # widgets
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        QToolBar.__init__(self)
        self.update_action = self.addAction("Update Database", self.rebuild_btn_clicked)
        self.update_action.setIcon(QIcon(str(icons.HARD_DRIVE)))
        self.update_action.setToolTip("Update Database")
        self.addSeparator()

        self.pref_action = self.addAction(
            "Preferences", self.preferences_action_clicked
        )
        self.pref_action.setIcon(QIcon(str(icons.PREFERENCE)))
        self.pref_action.setToolTip("Settings")
        self.addSeparator()

        self.addWidget(self.spacer)
        self.quit_action = self.addAction("Quit", self.quit_app)
        self.quit_action.setIcon(QIcon(str(icons.LOGOUT)))
        self.quit_action.setToolTip("close application")

    def quit_app(self):
        """quit the application gracefully"""
        self.file_worker.terminate()
        self.file_worker.wait()
        QCoreApplication.quit()

    def work_done(self):
        """propagate worker signal"""
        self.worker_finished.emit()

    def update_finished(self):
        """Update finished signal."""
        self.dbUpdated.emit("Database updated")

    def rebuild_btn_clicked(self):
        """Update the entire database."""
        self.dbUpdated.emit("Updating DB ...")
        self.thread = Worker(self)
        self.thread.finished.connect(self.work_done)
        self.thread.start()

    def preferences_action_clicked(self):
        """Preference dialog button click event."""
        self.preferences = PreferenceDialog()

    def case_action_clicked(self):
        """Turn case sensitivity on or off"""
        b = self.case_action.isChecked()
        self.case_action.setChecked(b)
