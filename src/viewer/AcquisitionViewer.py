
import typing
import logging

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt

import numpy as np
import matplotlib as plt

from matplotlib.backends.backend_qt5agg import FigureCanvas


acquisition_header_fields = [
    ('version', 'Version', "ISMRMRD Version"),
    ('flags', 'Flags', "Acquisition flags bitfield."),
    ('measurement_uid', 'UID', "Unique ID for the measurement."),
    ('scan_counter', 'Scan Counter', "Current acquisition number in the measurement."),
    ('acquisition_time_stamp', 'Acquisition Timestamp', "Acquisition Timestamp"),
    ('physiology_time_stamp', 'Physiology Timestamps', "Physiology Timestamps (e.g. ecg, breathing, etc.)"),
    ('number_of_samples', 'Samples', "Number of samples acquired."),
    ('available_channels', 'Available Channels', "Number of available channels."),
    ('active_channels', 'Active Channels', "Number of channels currently active."),
    ('channel_mask', 'Channel Mask', "A binary mask indicating which channels are active."),
    ('discard_pre', 'Prefix Discard', "Samples to be discarded at the beginning of the acquisition."),
    ('discard_post', 'Postfix Discard', "Samples to be discarded at the end of the acquisition."),
    ('center_sample', 'Center Sample', "Sample at the center of k-space."),
    ('encoding_space_ref', 'Encoding Space', "Acquisition encoding space reference."),
    ('trajectory_dimensions', 'Trajectory Dimensions', "Dimensionality of the trajectory vector."),
    ('sample_time_us', 'Sample Time', "Time between samples (in microseconds), sampling BW."),
    ('position', 'Position', "Three-dimensional spacial offsets from isocenter."),
    ('read_dir', 'Read Direction', "Directional cosines of the readout/frequency encoding."),
    ('phase_dir', 'Phase Direction', "Directional cosines of the phase."),
    ('slice_dir', 'Slice Direction', "Directional cosines of the slice direction."),
    ('patient_table_position', 'Patient Table', "Patient table off-center."),
    ('idx', 'Encoding Counters', "Encoding Counters"),
    ('user_int', 'User Integers', "Free user parameters."),
    ('user_float', 'User Floats', "Free user parameters.")
]


class AcquisitionModel(QtCore.QAbstractTableModel):

    def __init__(self, container):
        super().__init__()
        self.acquisitions = list(container.acquisitions)

        self.data_handlers = {
            'idx': self.__encoding_counters_handler,
            'physiology_time_stamp': self.__array_handler,
            'channel_mask': self.__array_handler,
            'position': self.__array_handler,
            'read_dir': self.__array_handler,
            'phase_dir': self.__array_handler,
            'slice_dir': self.__array_handler,
            'patient_table_position': self.__array_handler,
            'user_int': self.__array_handler,
            'user_float': self.__array_handler
        }

    def rowCount(self, _=None) -> int:
        return len(self.acquisitions)

    def columnCount(self, _=None) -> int:
        return len(acquisition_header_fields)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> typing.Any:

        if orientation == Qt.Orientation.Vertical:
            return None

        _, header, tooltip = acquisition_header_fields[section]

        if role == Qt.DisplayRole:
            return header
        if role == Qt.ToolTipRole:
            return tooltip

        return None

    def data(self, index: QtCore.QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        acquisition = self.acquisitions[index.row()]
        attribute, _, tooltip = acquisition_header_fields[index.column()]

        handler = self.data_handlers.get(attribute, lambda x: x)

        if role == Qt.DisplayRole:
            return handler(getattr(acquisition, attribute))
        if role == Qt.ToolTipRole:
            return tooltip

        return None

    def __array_handler(self, array):
        return ', '.join([str(item) for item in array])

    def __encoding_counters_handler(self, _):
        return "Not Displayed"


class AcquisitionViewer(QtWidgets.QSplitter):

    def __init__(self, container):
        super().__init__()

        self.model = AcquisitionModel(container)

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


