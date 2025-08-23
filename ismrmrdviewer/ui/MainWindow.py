
import os
import logging
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Slot

from .FileWidget import FileWidget


class MainWindow(QtWidgets.QMainWindow):

    open = Signal(str)

    def __init__(self):
        super().__init__()

        self.setUnifiedTitleAndToolBarOnMac(True)

        self.fileMenu = super().menuBar().addMenu("&File")
        self.fileMenu.addAction("&Open", self.open_file_dialog)

        self.open.connect(self.open_file)

    @Slot()
    def open_file_dialog(self):

        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open ISMRMRD Data File",
            os.getcwd(),
            "ISMRMRD Data Files (*.h5 *.mrd);;All Files (*)"
        )

        if not file_name:
            return

        self.open.emit(file_name)

    def open_file(self, file_name):
        logging.info(f"Opening file: {file_name}")
        self.setWindowFilePath(file_name)
        self.setCentralWidget(FileWidget(self, file_name))


