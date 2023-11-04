"""
Module to provide QT icon related functionality
"""

from PySide2.QtWidgets import QFileIconProvider


class IconProvider(QFileIconProvider):
    "Qt Iconprovider subclass for the filename in the tableview."

    def icon(self, fileinfo):
        "returns the files icon."
        return QFileIconProvider.icon(self, fileinfo)
