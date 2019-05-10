
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
    ('idx.kspace_encode_step_1', 'Encode Step1', "Encoding Counters"),
    ('idx.kspace_encode_step_2', 'Encode Step2', "Encoding Counters"),
    ('idx.average', 'Average', "Encoding Counters"),
    ('idx.slice', 'Slice', "Encoding Counters"),
    ('idx.contrast', 'Contrast', "Encoding Counters"),
    ('idx.phase', 'Phase', "Encoding Counters"),
    ('idx.repetition', 'Repetition', "Encoding Counters"),
    ('idx.set', 'Set', "Encoding Counters"),
    ('idx.segment', 'Segment', "Encoding Counters"),
    ('idx.user', 'User', "Encoding Counters"),
    ('user_int', 'User Integers', "Free user parameters."),
    ('user_float', 'User Floats', "Free user parameters.")
]


class AcquisitionModel(QtCore.QAbstractTableModel):

    def __init__(self, container):
        super().__init__()
        self.acquisitions = list(container.acquisitions)

        self.data_handlers = {
            'idx.kspace_encode_step_1': self.__encoding_counters_handler,
            'idx.kspace_encode_step_2': self.__encoding_counters_handler,
            'idx.average': self.__encoding_counters_handler,
            'idx.slice': self.__encoding_counters_handler,
            'idx.contrast': self.__encoding_counters_handler,
            'idx.phase': self.__encoding_counters_handler,
            'idx.repetition': self.__encoding_counters_handler,
            'idx.set': self.__encoding_counters_handler,
            'idx.segment': self.__encoding_counters_handler,
            'idx.user': self.__user_encoding_counters_handler,
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

    def rowCount(self, _=None):
        return len(self.acquisitions)

    def columnCount(self, _=None):
        return len(acquisition_header_fields)

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if orientation == Qt.Orientation.Vertical:
            return None

        _, header, tooltip = acquisition_header_fields[section]

        if role == Qt.DisplayRole:
            return header
        if role == Qt.ToolTipRole:
            return tooltip

        return None

    def data(self, index, role=Qt.DisplayRole):
        acquisition = self.acquisitions[index.row()]
        attribute, _, tooltip = acquisition_header_fields[index.column()]

        handler = self.data_handlers.get(attribute, lambda acq,attr: getattr(acq,attr))

        if role == Qt.DisplayRole:
            return handler(acquisition, attribute)
        if role == Qt.ToolTipRole:
            return tooltip

        return None

    def __array_handler(self, acquisition,attribute):
        array = getattr(acquisition,attribute)
        return ', '.join([str(item) for item in array])

    @staticmethod
    def __encoding_counters_handler(acquisition, attribute):
        return getattr(acquisition.idx,attribute[4:])

    @staticmethod
    def __user_encoding_counters_handler(acquisition, attribute):
        array = getattr(acquisition.idx, attribute[4:])
        return ', '.join([str(item) for item in array])


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

        print(acquisition.data.shape)
