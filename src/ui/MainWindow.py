
import os

from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot, SIGNAL, SLOT


class MainWindow(QtWidgets.QMainWindow):

    open = Signal(str)

    def __init__(self):
        super().__init__()

        self.fileMenu = super().menuBar().addMenu("&File")
        open_action = self.fileMenu.addAction("&Open")
        open_action.connect(SIGNAL('triggered()'), self, SLOT('open_file_dialog()'))

    @Slot()
    def open_file_dialog(self):

        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open ISMRMRD Data File",
            os.getcwd(),
            "ISMRMRD Data Files (*.h5)"
        )

        self.open.emit(file_name)
