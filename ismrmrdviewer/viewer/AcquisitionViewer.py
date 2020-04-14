import logging

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.figure as figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

acquisition_header_fields = [
    ('version', 'Version', "ISMRMRD Version"),
    ('flags', 'Flags', "Acquisition flags bitfield."),
    ('measurement_uid', 'UID', "Unique ID for the measurement."),
    ('scan_counter', 'Scan Counter', "Current acquisition number in the measurement."),
    ('idx.kspace_encode_step_1', 'Encode Step1', "Encoding Counters"),
    ('idx.kspace_encode_step_2', 'Encode Step2', "Encoding Counters"),
    ('idx.average', 'Average', "Encoding Counters"),
    ('idx.slice', 'Slice', "Encoding Counters"),
    ('idx.contrast', 'Contrast', "Encoding Counters"),
    ('idx.phase', 'Phase', "Encoding Counters"),
    ('idx.repetition', 'Repetition', "Encoding Counters"),
    ('idx.set', 'Set', "Encoding Counters"),
    ('idx.segment', 'Segment', "Encoding Counters"),    ('acquisition_time_stamp', 'Acquisition Timestamp', "Acquisition Timestamp"),
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
    ('idx.user', 'User Idx', "Encoding Counters"),
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

    def num_coils(self):
        return self.acquisitions[0].active_channels

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


class AcquisitionTable(QtWidgets.QTableView):
    selection_changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)

        self.selection_changed.emit()


class AcquisitionControlGUI(QtWidgets.QWidget):

    def __init__(self,num_channels):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.data_processing = QtWidgets.QComboBox()
        self.data_processing.addItem("Mag./Phase", userData={"names": ("Magnitude", "Phase"),
                                                             "transform": lambda x: (np.abs(x), np.angle(x))})
        self.data_processing.addItem("Real/Imag", userData={"names": ("Real", "Imag."),
                                                            "transform": lambda x: (np.real(x), np.imag(x))})
        layout.addWidget(self.data_processing)

        self.channel_selector = QtWidgets.QComboBox()
        self.__set_num_channels(num_channels)
        layout.addWidget(self.channel_selector)

        self.setLayout(layout)

    def __set_num_channels(self, num_channels):
        for i in range(self.channel_selector.count()):
            self.channel_selector.removeItem(i)

        for idx in range(num_channels):
            self.channel_selector.addItem("Channel " + str(idx), userData={"selector": lambda x, i=idx : x[:, i:i + 1],
                                                                         "labeler": lambda scan, coil: str(scan)})

        self.channel_selector.addItem("All Channels", userData={"selector": lambda x: x,
                                                                "labeler": lambda scan, coil: str((scan, coil))})

    def label(self, scan, coil):
        return self.channel_selector.currentData()["labeler"](scan, coil)

    def axes_titles(self):
        return self.data_processing.currentData()["names"]

    def transform_acquisition(self, acq):
        return self.data_processing.currentData()["transform"](self.channel_selector.currentData()["selector"](acq))


class AcquisitionPlotter(FigureCanvas):

    def __init__(self):

        self.figure = mpl.figure.Figure()
        self.axis = self.figure.subplots(2, 1, sharex='col')
        self.figure.subplots_adjust(hspace=0)

        self.legend = mpl.legend.Legend(self.figure, [], [])
        self.figure.legends.append(self.legend)
        super().__init__(self.figure)

    def clear(self):
        for ax in self.axis:
            ax.clear()

    def plot(self, acquisitions, formatter, labeler):

        for acquisition in acquisitions:
            acquisition1, acquisition2 = formatter(acquisition)
            x_step = acquisition.sample_time_us
            x_scale = np.arange(0, acquisition1.shape[0] * x_step, x_step)
            for coil, acq1 in enumerate(acquisition1.T):
                self.axis[0].plot(x_scale, acq1, label=labeler(acquisition.scan_counter, coil))
            self.axis[1].plot(x_scale, acquisition2)

        handles, labels = self.axis[0].get_legend_handles_labels()
        self.legend = mpl.legend.Legend(self.figure, handles, labels)
        self.figure.legends[0] = self.legend

        self.figure.canvas.draw()

    def set_titles(self, titles):
        for ax, title in zip(self.axis, titles):
            ax.set_title(title, loc="right", pad=-10)


class AcquisitionViewer(QtWidgets.QSplitter):

    def __init__(self, container):
        super().__init__()

        self.model = AcquisitionModel(container)

        self.acquisitions = AcquisitionTable(self)
        self.acquisitions.setModel(self.model)
        self.acquisitions.setAlternatingRowColors(True)
        self.acquisitions.resizeColumnsToContents()
        self.acquisitions.selection_changed.connect(self.selection_changed)
        self.acquisitions.pressed.connect(self.mouse_clicked)

        self.setOrientation(Qt.Vertical)

        self.canvas = AcquisitionPlotter()

        self.bottom_view = QtWidgets.QSplitter()
        self.acquisition_gui = AcquisitionControlGUI(self.model.num_coils())
        self.bottom_view.addWidget(self.acquisition_gui)
        self.acquisition_gui.data_processing.currentIndexChanged.connect(self.selection_changed)
        self.acquisition_gui.channel_selector.currentIndexChanged.connect(self.selection_changed)

        self.addWidget(self.acquisitions)
        self.addWidget(self.canvas)
        self.addWidget(self.bottom_view)

        self.navigation_toolbar = NavigationToolbar(self.canvas, self.bottom_view)
        self.bottom_view.addWidget(self.navigation_toolbar)

        self.setStretchFactor(0, 6)
        self.setStretchFactor(1, 1)

    def table_clicked(self, index):
        acquisition = self.model.acquisitions[index.row()]
        self.plot([acquisition])

    def format_data(self, acq):
        return self.acquisition_gui.transform_acquisition(acq.data.T)

    def selection_changed(self):
        self.canvas.clear()
        self.canvas.set_titles(self.acquisition_gui.axes_titles())

        indices = set([idx.row() for idx in self.acquisitions.selectedIndexes()])
        acquisitions = [self.model.acquisitions[idx] for idx in
                        indices]
        self.canvas.plot(acquisitions, self.format_data, self.acquisition_gui.label)

    def mouse_clicked(self, index):
        if not QtGui.QGuiApplication.mouseButtons() & Qt.RightButton:
            return
        menu = QtWidgets.QMenu(self)
        DeleteAction = QtWidgets.QAction('Delete', self)
        y = index.column()
        DeleteAction.triggered.connect(lambda: self.acquisitions.hideColumn(y))
        menu.addAction(DeleteAction)
        menu.popup(QtGui.QCursor.pos())

        # SortAction = QtWidgets.QAction('Sort', self)
        # menu.addAction(SortAction)
        menu.popup(QtGui.QCursor.pos())
