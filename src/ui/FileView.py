
import ismrmrd

from PySide2 import QtWidgets
from viewer import HeaderViewer, ImageViewer, AcquisitionViewer, WaveformViewer


class ContentTree(QtWidgets.QTreeWidget):

    def __init__(self, parent, file):
        super().__init__(parent)

        self.__populate_tree(self, file)

        self.setHeaderHidden(True)
        self.itemDoubleClicked.connect(lambda widget, _: parent.set_viewer(widget.container, widget.viewer))

    def __populate_tree(self, node, container):

        for item in container:

            child = QtWidgets.QTreeWidgetItem(node, [item])
            child.setExpanded(True)

            for content, viewer in self.__available_contents(container[item]):
                content = QtWidgets.QTreeWidgetItem(child, [content])
                content.container = container[item]
                content.viewer = viewer

            self.__populate_tree(child, container[item])

    @staticmethod
    def __available_contents(container):

        def header():
            if container.has_header():
                return 'Header', HeaderViewer

        def images():
            if container.has_images():
                return 'Images', ImageViewer

        def acquisitions():
            if container.has_acquisitions():
                return 'Acquisitions', AcquisitionViewer

        def waveforms():
            if container.has_waveforms():
                return 'Waveforms', WaveformViewer

        return filter(lambda a: a is not None, [header(), acquisitions(), waveforms(), images()])


class FileView(QtWidgets.QSplitter):

    def __init__(self, parent, file_name):
        super().__init__(parent)

        self.file_name = file_name
        self.file = ismrmrd.File(file_name, mode='r')

        self.viewer = QtWidgets.QListWidget(self)
        self.addWidget(ContentTree(self, self.file))
        self.addWidget(self.viewer)

        self.__balance()

    def set_viewer(self, container, factory):
        viewer = factory(container)
        self.replaceWidget(1, viewer)
        self.viewer = viewer

        self.__balance()

    def __balance(self):
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 4)
