import logging

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.figure as figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from .utils import CachedDataset




def __acquisition_flag_names():
    names = {
    0x01 << 0: 'ENCODE_STEP1::first',
    0x01 << 1: 'ENCODE_STEP1::last',
    0x01 << 2: 'ENCODE_STEP2::first',
    0x01 << 3: 'ENCODE_STEP2::last',
    0x01 << 4: 'AVERAGE::first',
    0x01 << 5: 'AVERAGE::last',
    0x01 << 6: 'SLICE::first',
    0x01 << 7: 'SLICE::last',
    0x01 << 8: 'CONTRAST::first',
    0x01 << 9: 'CONTRAST::last',
    0x01 << 10: 'PHASE::first',
    0x01 << 11: 'PHASE::last',
    0x01 << 12: 'REPETITION::first',
    0x01 << 13: 'REPETITION::last',
    0x01 << 14: 'SET::first',
    0x01 << 15: 'SET::last',
    0x01 << 16: 'SEGMENT::first',
    0x01 << 17: 'SEGMENT::last',
    0x01 << 18: 'NOISE_MEASUREMENT',
    0x01 << 19: 'PARALLEL_CALIBRATION',
    0x01 << 20: 'PARALLEL_CALIBRATION_AND_IMAGING',
    0x01 << 21: 'REVERSE',
    0x01 << 22: 'NAVIGATION_DATA',
    0x01 << 23: 'PHASE_CORRECTION_DATA',
    0x01 << 24: 'MEASUREMENT::last',
    0x01 << 25: 'HP_FEEDBACK_DATA',
    0x01 << 26: 'DUMMY_DATA',
    0x01 << 27: 'RT_FEEDBACK_DATA',
    0x01 << 28: 'SURFACE_COIL_CORRECTION_DATA',
    0x01 << 29: 'PHASE_STABILIZATION_REFERENCE',
    0x01 << 30: 'PHASE_STABILIZATION',

    0x01 << 52: 'COMPRESSION::1',
    0x01 << 53: 'COMPRESSION::2',
    0x01 << 54: 'COMPRESSION::3',
    0x01 << 55: 'COMPRESSION::4',

    0x01 << 56: 'USER::1',
    0x01 << 57: 'USER::2',
    0x01 << 58: 'USER::3',
    0x01 << 59: 'USER::4',
    0x01 << 60: 'USER::5',
    0x01 << 61: 'USER::6',
    0x01 << 62: 'USER::7',
    0x01 << 63: 'USER::8',
    }

    for i in range(31,52):
        names[0x01 << i] = f'UNKNOWN::{i}'
    return names 


acquisition_flags = __acquisition_flag_names() 


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
        self.acquisitions = CachedDataset(container.acquisitions)

        self.data_handlers = {
            'flags': self.__flags_handler,
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
        attribute, _, tooltip = acquisition_header_fields[index.column()]

        if role == Qt.DisplayRole:
            acquisition = self.acquisitions[index.row()]
            handler = self.data_handlers.get(attribute, lambda acq, attr: getattr(acq, attr))
            return handler(acquisition, attribute)
        if role == Qt.ToolTipRole:
            if attribute == 'flags':
                # decode flag names from bitfield
                acquisition = self.acquisitions[index.row()]
                flags = self.acquisitions[index.row()].flags
                tooltip = self.__get_flags_tooltip(flags)

            return tooltip

        return None

    def num_coils(self):
        return self.acquisitions[0].active_channels

    @staticmethod
    def __flag_labels(flags):
        return [label for flag,label in  acquisition_flags.items() if flags & flag]        

    @staticmethod
    def __flags_handler(acquisition, attribute):
        return ', '.join(AcquisitionModel.__flag_labels(getattr(acquisition,attribute)))

    @staticmethod
    def __array_handler(acquisition, attribute):
        array = getattr(acquisition, attribute)
        return ', '.join([str(item) for item in array])

    @staticmethod
    def __encoding_counters_handler(acquisition, attribute):
        return getattr(acquisition.idx, attribute[4:])

    @staticmethod
    def __user_encoding_counters_handler(acquisition, attribute):
        array = getattr(acquisition.idx, attribute[4:])
        return ', '.join([str(item) for item in array])
    
  
    @staticmethod
    def __get_flags_tooltip(flags):
        labels = AcquisitionModel.__flag_labels(flags)
        tooltip = '\n'.join(labels)
        if not tooltip:
            # fill empty tooltip
            tooltip = "No flags set"
  
        return tooltip


class AcquisitionTable(QtWidgets.QTableView):
    selection_changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        self.selection_changed.emit()


class AcquisitionControlGUI(QtWidgets.QWidget):

    def __init__(self, num_channels):
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
            ax.set_title(title, loc="right")


class TrajectoryControlGUI(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QHBoxLayout()
        self.trajectory_selector = QtWidgets.QComboBox()
        layout.addWidget(self.trajectory_selector)

        self.setLayout(layout)

    def update_available_trajectory_dimensions(self, acquisitions):
        available = max([acq.traj.shape[1] for acq in acquisitions])

        selected = self.trajectory_selector.currentIndex()

        self.trajectory_selector.clear()
        for dim in range(available):
            self.trajectory_selector.addItem("Dimension: " + str(dim),
                                             userData=(dim, lambda acq, d: str((acq.scan_counter, d))))

        self.trajectory_selector.setCurrentIndex(selected)

    def select(self, acquisition):
        dim, labeller = self.trajectory_selector.currentData() or self.trajectory_selector.itemData(0)
        return acquisition.traj[:, dim], labeller(acquisition, dim)


class TrajectoryPlotter(FigureCanvas):

    def __init__(self):
        self.figure = mpl.figure.Figure()
        self.axis = self.figure.subplots(1, 1)
        self.legend = mpl.legend.Legend(self.figure, [], [])
        self.figure.legends.append(self.legend)
        super().__init__(self.figure)

    def clear(self):
        self.axis.clear()

    def plot(self, acquisitions, select):

        for acquisition in acquisitions:

            if acquisition.traj.size == 0:
                continue

            x_step = acquisition.sample_time_us
            x_scale = np.arange(0, acquisition.traj.shape[0] * x_step, x_step)
            trajectory, label = select(acquisition)
            self.axis.plot(x_scale, trajectory, label=label)

        handles, labels = self.axis.get_legend_handles_labels()
        self.legend = mpl.legend.Legend(self.figure, handles, labels)
        self.figure.legends = [self.legend]
        self.figure.canvas.draw()

    def set_title(self, title):
        self.axis.set_title(title, loc="right")


class AcquisitionViewer(QtWidgets.QSplitter):

    def __init__(self, container):
        super().__init__()

        self.model = AcquisitionModel(container)

        self.acquisitions = AcquisitionTable(self)
        self.acquisitions.setModel(self.model)
        self.acquisitions.setAlternatingRowColors(True)
        self.acquisitions.resizeColumnsToContents()
        self.acquisitions.setColumnWidth(1, 96)  # Start the flags out small; full width is a little ostentatious.
        self.acquisitions.selection_changed.connect(self.selection_changed)
        self.acquisitions.pressed.connect(self.mouse_clicked)

        self.setOrientation(Qt.Vertical)

        def create_panel(canvas, control):
            splitter = QtWidgets.QSplitter()
            splitter.setOrientation(Qt.Vertical)

            layout = QtWidgets.QSplitter()
            layout.addWidget(control)
            layout.addWidget(NavigationToolbar(canvas, layout))

            splitter.addWidget(canvas)
            splitter.addWidget(layout)

            return splitter

        def create_data_panel():
            self.canvas = AcquisitionPlotter()
            self.acquisition_gui = AcquisitionControlGUI(self.model.num_coils())

            self.acquisition_gui.data_processing.currentIndexChanged.connect(self.selection_changed)
            self.acquisition_gui.channel_selector.currentIndexChanged.connect(self.selection_changed)

            return create_panel(self.canvas, self.acquisition_gui)

        def create_trajectory_panel():
            self.trajectory_canvas = TrajectoryPlotter()
            self.trajectory_gui = TrajectoryControlGUI()

            self.trajectory_gui.trajectory_selector.currentIndexChanged.connect(self.selection_changed)

            return create_panel(self.trajectory_canvas, self.trajectory_gui)

        self.data_panel = create_data_panel()
        self.trajectory_panel = create_trajectory_panel()

        self.addWidget(self.acquisitions)
        self.addWidget(self.data_panel)
        self.addWidget(self.trajectory_panel)

        self.setStretchFactor(0, 6)
        self.setStretchFactor(1, 1)
        self.setStretchFactor(2, 1)

    def table_clicked(self, index):
        acquisition = self.model.acquisitions[index.row()]
        self.plot([acquisition])

    def format_data(self, acq):
        return self.acquisition_gui.transform_acquisition(acq.data.T)

    def selection_changed(self):
        indices = set([idx.row() for idx in self.acquisitions.selectedIndexes()])
        acquisitions = [self.model.acquisitions[idx] for idx in indices]

        self.update_canvas(acquisitions)
        self.update_trajectory(acquisitions)

    def update_canvas(self, acquisitions):
        self.canvas.clear()
        self.canvas.set_titles(self.acquisition_gui.axes_titles())
        self.canvas.plot(acquisitions, self.format_data, self.acquisition_gui.label)

    def update_trajectory(self, acquisitions):
        self.trajectory_panel.setVisible(any(acquisition.trajectory_dimensions for acquisition in acquisitions))
        self.update_trajectory_gui(acquisitions)
        self.update_trajectory_canvas(acquisitions)

    def update_trajectory_gui(self, acquisitions):
        self.trajectory_gui.trajectory_selector.currentIndexChanged.disconnect(self.selection_changed)
        self.trajectory_gui.update_available_trajectory_dimensions(acquisitions)
        self.trajectory_gui.trajectory_selector.currentIndexChanged.connect(self.selection_changed)

    def update_trajectory_canvas(self, acquisitions):
        self.trajectory_canvas.clear()
        self.trajectory_canvas.set_title("Trajectory")
        self.trajectory_canvas.plot(acquisitions, self.trajectory_gui.select)

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
