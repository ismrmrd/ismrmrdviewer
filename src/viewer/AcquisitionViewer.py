
import typing
import logging
import datetime

from PySide2 import QtWidgets, QtCore, QtCharts, QtGui
from PySide2.QtCore import Qt

acquisition_header_fields = [
    ('version', 'Version', "ISMRMRD Version"),
    ('flags', 'Flags', "Acquisition flags bitfield."),
    ('measurement_uid', 'UID', "Unique ID for the measurement."),
    ('scan_counter', 'Scan Counter', "Current acquisition number in the measurement."),
    ('acquisition_time_stamp', 'Acquisition Timestamp', None),
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
    ('idx', 'Encoding Counters', None),
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

        self.chart = QtCharts.QtCharts.QChart()
        self.chart.createDefaultAxes()

        self.acquisition_view = QtWidgets.QTableView(self)
        self.acquisition_view.setModel(self.model)
        self.acquisition_view.setAlternatingRowColors(True)
        self.acquisition_view.resizeColumnsToContents()

        self.chart_view = QtCharts.QtCharts.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

        self.setOrientation(Qt.Vertical)
        self.addWidget(self.acquisition_view)
        self.addWidget(self.chart_view)

