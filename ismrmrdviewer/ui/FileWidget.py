
import ismrmrd

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QCursor
from ismrmrdviewer.viewer import HeaderViewer, ImageViewer, AcquisitionViewer, WaveformViewer


class FileWidget(QtWidgets.QSplitter):

    def __init__(self, parent, file_name):
        super().__init__(parent)

        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(lambda widget, _: self.set_viewer(widget.container, widget.viewer))

        FileWidget.__populate_tree(self.tree, ismrmrd.File(file_name, mode='r'))

        self.viewer = QtWidgets.QListWidget(self)

        self.addWidget(self.tree)
        self.addWidget(self.viewer)

        self.__balance()

    def set_viewer(self, container, factory):
        QGuiApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        viewer = factory(container)
        self.replaceWidget(1, viewer)
        self.viewer = viewer

        self.__balance()
        QGuiApplication.restoreOverrideCursor()

    def __balance(self):
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 4)

    @staticmethod
    def __available_contents(container):

        viewers = {
            'header': ('Header', HeaderViewer),
            'images': ('Images', ImageViewer),
            'waveforms': ('Waveforms', WaveformViewer),
            'acquisitions': ('Acquisitions', AcquisitionViewer)
        }

        return [viewers[key] for key in container.available()]

    @staticmethod
    def __populate_tree(node, container):

        for item in container:

            child = QtWidgets.QTreeWidgetItem(node, [item])
            child.setExpanded(True)

            for content, viewer in FileWidget.__available_contents(container[item]):
                content = QtWidgets.QTreeWidgetItem(child, [content])
                content.container = container[item]
                content.viewer = viewer

            FileWidget.__populate_tree(child, container[item])
