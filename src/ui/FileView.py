
import os.path

import logging
import ismrmrd

from PySide2 import QtWidgets


class FileView(QtWidgets.QWidget):

    def __init__(self, parent, file_name):
        super().__init__(parent)

        self.file_name = file_name
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QtWidgets.QTreeView(self))
        self.layout.addWidget(QtWidgets.QListView(self))


