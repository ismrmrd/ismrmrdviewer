
import typing
import logging

from PySide2 import QtWidgets, QtCore
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

        self.data_role_handlers = {
            Qt.DisplayRole: self.display_handler,
            Qt.ToolTipRole: self.tooltip_handler,
            Qt.TextAlignmentRole: self.alignment_handler
        }

        self.display_handlers = {
            'physiology_time_stamp': self.display_array,
            'channel_mask': self.display_channel_mask,
            'position': self.display_array,
            'read_dir': self.display_array,
            'phase_dir': self.display_array,
            'slice_dir': self.display_array,
            'patient_table_position': self.display_array,
            'user_int': self.display_array,
            'user_float': self.display_array,
            'idx': self.display_encoding_counters
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

    def default_role_handler(self, _, __, ___):
        return None

    def tooltip_handler(self, _, __, tooltip):
        return tooltip

    def alignment_handler(self, _, __, ___):
        return Qt.AlignmentFlag.AlignVCenter

    def display_array(self, array):
        return ', '.join([str(item) for item in array])

    def display_channel_mask(self, channel_mask):
        return self.display_array(channel_mask)

    def display_encoding_counters(self, _):
        return 'Not Displayed'

    def display_handler(self, acquisition, attribute, ___):
        handler = self.display_handlers.get(attribute, str)
        return handler(getattr(acquisition, attribute))

    def data(self, index: QtCore.QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        acquisition = self.acquisitions[index.row()]
        attribute, _, tooltip = acquisition_header_fields[index.column()]

        handler = self.data_role_handlers.get(role, self.default_role_handler)
        return handler(acquisition, attribute, tooltip)


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


