
import logging

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt

import numpy as np
import matplotlib as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas

# RR: example waveform headers are not arrays
waveform_header_fields = [
    ('version', 'Version', "ISMRMRD Version"),
    ('flags', 'Flags', "Acquisition flags bitfield."),
    ('measurement_uid', 'UID', "Unique ID for the measurement."),
    ('scan_counter', 'Scan Counter', "Current acquisition number in the measurement."),
    ('time_stamp', 'Acquisition Timestamp', "Acquisition Timestamp"),
    ('number_of_samples', 'Samples', "Number of samples."),
    ('channels', 'Number of Channels', "Number of channels."),
    ('sample_time_us', 'Sample Time', "Time between samples (in microseconds)"),
    ('waveform_id', 'Waveform ID', "Waveform ID.")
]

class WaveformModel(QtCore.QAbstractTableModel):

    def __init__(self, container):
        super().__init__()

        self.container = container
        self.acquisitions = list(container.waveforms)

        logging.info("Waveform constructor.")

        # self.data_handlers = {
        #     'version': self.__array_handler,
        #     'flags': self.__array_handler,
        #     'measurement_uid': self.__array_handler,
        #     'scan_counter': self.__array_handler,
        #     'time_stamp': self.__array_handler,
        #     'number_of_samples': self.__array_handler,
        #     'number_of_channels': self.__array_handler,
        #     'sample_time_us': self.__array_handler,
        #     'waveform_id': self.__array_handler,
        # }

    def rowCount(self, _=None):
        return len(self.acquisitions)

    def columnCount(self, _=None):
        return len(waveform_header_fields)

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if orientation == Qt.Orientation.Vertical:
            return None

        _, header, tooltip = waveform_header_fields[section]

        if role == Qt.DisplayRole:
            return header
        if role == Qt.ToolTipRole:
            return tooltip

        return None

    def data(self, index, role=Qt.DisplayRole):
        acquisition = self.acquisitions[index.row()]
        attribute, _, tooltip = waveform_header_fields[index.column()]

        if role == Qt.DisplayRole:
            return getattr(acquisition,attribute)
        if role == Qt.ToolTipRole:
            return tooltip

        return None

class WaveformViewer(QtWidgets.QSplitter):

    def __init__(self, container):
        super().__init__()

        self.model = WaveformModel(container)

        self.figure = plt.figure.Figure()
        self.canvas = FigureCanvas(self.figure)

        self.acquisitions = QtWidgets.QTableView(self)
        self.acquisitions.setModel(self.model)
        self.acquisitions.setAlternatingRowColors(True)
        self.acquisitions.resizeColumnsToContents()
        self.acquisitions.clicked.connect(self.table_clicked)

        self.setOrientation(Qt.Vertical)
        self.addWidget(self.acquisitions)
        self.addWidget(self.canvas)

        self.setStretchFactor(0, 6)
        self.setStretchFactor(1, 1)

    def table_clicked(self, index):
        acquisition = self.model.acquisitions[index.row()]
        self.plot(acquisition)

    def plot(self, acquisition):
        logging.info(f"Plotting acquisition {{scan_counter={acquisition.scan_counter}}}")

        print(acquisition.data.shape)
