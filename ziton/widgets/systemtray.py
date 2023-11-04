import ziton.icons as icons
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMenu, QSystemTrayIcon

print(icons.LOGO)


class Systemtray(QSystemTrayIcon):
    """Custom systemtray implementation"""

    def __init__(self, parent=None):
        """Initialises Systemtray widget"""
        QSystemTrayIcon.__init__(self)
        self._icon = QIcon(str(icons.LOGO))
        self.setIcon(self._icon)
        self._menu = QMenu()
        self.setContextMenu(self._menu)
