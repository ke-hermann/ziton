"""
Monitors filesystem status in realtime.
"""

import logging
import os

import inotify.adapters
from PySide2.QtCore import QObject, QThread, Signal, Slot

from ziton.config import hidden_files_enabled, included_directories

LOGGER = logging.getLogger(__name__)


def get_subdirs():
    """get all subdirectories"""
    check_hidden = hidden_files_enabled()
    directories = included_directories()
    dir_list = []
    for directory in directories:
        for root, dirs, _ in os.walk(directory, topdown=True):
            if not check_hidden:
                dirs[:] = [d for d in dirs if not d[0] == "."]
            dir_list.extend([os.path.join(root, d) for d in dirs])
    return dir_list


class Worker(QThread):
    """
    Worker thread
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot()
    def run(self):
        """start worker."""
        for event in self.parent().ino.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event

            if "IN_CREATE" in type_names:
                p = os.path.join(path, filename)
                self.parent().file_created(p)
            if "IN_DELETE" in type_names:
                p = os.path.join(path, filename)
                self.parent().file_deleted(p)


class FileMonitor(QObject):

    fileAdded = Signal(str)
    fileDeleted = Signal(str)

    def __init__(self):
        """Initialises the file monitor"""
        QObject.__init__(self)
        self.directories = get_subdirs()
        self.ino = inotify.adapters.Inotify()
        self.add_watchers()
        self.worker = Worker(self)

    def file_created(self, filepath):
        """Forward file creation signal"""
        self.fileAdded.emit(filepath)

    def file_deleted(self, filepath):
        """Forward file deletion signal"""
        self.fileDeleted.emit(filepath)

    def add_watchers(self):
        """Add directories to inotify watch instance"""
        for d in self.directories:
            self.ino.add_watch(d)
        l = len(self.directories)
        LOGGER.info(f"Starting to monitor {l} directories...")
