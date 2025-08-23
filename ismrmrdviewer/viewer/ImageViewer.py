import logging
import numpy
import pdb
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

from PySide6 import QtCore, QtGui, QtWidgets as QTW

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

DIMS = ('Instance', 'Channel', 'Slice')

class ImageViewer(QTW.QWidget):

    def __init__(self, container):
        """
        Stores off container for later use; sets up the main panel display
        canvas for plotting into with matplotlib. Also prepares the interface
        for working with multi-dimensional data.
        """
        super().__init__()

        self.container = container
        logging.info("Image constructor.")

        # Main layout
        layout = QTW.QVBoxLayout(self)

        self.nimg = len(self.container.images)

        # Dimension controls; Add a widget with a horizontal layout
        cw = QTW.QWidget()
        layout.addWidget(cw)
        controls = QTW.QHBoxLayout(cw)
        controls.setContentsMargins(0,0,0,0)

        # Create a drop-down for the image instance
        self.selected = {}
        for dim in DIMS:
            controls.addWidget(QTW.QLabel("{}:".format(dim)))
            self.selected[dim] = QTW.QSpinBox()
            controls.addWidget(self.selected[dim])
            self.selected[dim].valueChanged.connect(self.update_image)
        self.selected['Instance'].setMaximum(self.nimg - 1)

        self.animate = QTW.QCheckBox("Animate:")
        controls.addWidget(self.animate)

        self.animDim = QTW.QComboBox()
        for dim in DIMS:
            self.animDim.addItem(dim)
        controls.addWidget(self.animDim)
        controls.addStretch()

        self.animate.stateChanged.connect(self.animation)
        self.animDim.currentIndexChanged.connect(self.check_dim)

        # Window/level controls; Add a widget with a horizontal layout
        # NOTE: we re-use the local names from above...
        cw = QTW.QWidget()
        layout.addWidget(cw)
        controls = QTW.QHBoxLayout(cw)
        controls.setContentsMargins(0,0,0,0)

        self.windowScaled = QTW.QDoubleSpinBox()
        self.windowScaled.setRange(-2**31, 2**31 - 1)
        self.levelScaled = QTW.QDoubleSpinBox()
        self.levelScaled.setRange(-2**31, 2**31 - 1)
        controls.addWidget(QTW.QLabel("Window:"))
        controls.addWidget(self.windowScaled)
        controls.addWidget(QTW.QLabel("Level:"))
        controls.addWidget(self.levelScaled)
        controls.addStretch()

        self.windowScaled.valueChanged.connect(self.window_input)
        self.levelScaled.valueChanged.connect(self.level_input)

        layout.setContentsMargins(0,0,0,0)
        self.fig = Figure(figsize=(6,6),
                          dpi=72,
                          facecolor=(1,1,1),
                          edgecolor=(0,0,0),
                          tight_layout=True)

        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.canvas.setSizePolicy(QTW.QSizePolicy.Expanding,
                                  QTW.QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

        self.label_base = "A{:d}/S{:d}/C{:d}/P{:d}/R{:d}/S{:d}"
        self.label = QTW.QLabel("")
        self.label.setMaximumSize(140, 20)

        layout.addWidget(self.label)


        
        self.stack = numpy.array(self.container.images.data)
        if self.stack.shape[0] == 1:
            self.animate.setEnabled(False)

        logging.info("Container size {}".format(str(self.stack.shape)))

        # Window/Level support
        self.min = self.stack.min()
        self.max = self.stack.max()
        self.range = self.max - self.min

        v1 = numpy.percentile(self.stack,2)
        v2 = numpy.percentile(self.stack,98)
        self.window = (v2-v1)/self.range
        self.level = (v2+v1)/2/self.range

        self.mloc = None

        # For animation
        self.timer = None

        self.selected['Channel'].setMaximum(len(self.stack[0]) - 1)
        self.selected['Slice'].setMaximum(len(self.stack[0][0]) - 1)

        self.update_image()

        for (cont, var) in ((self.windowScaled, self.window),
                            (self.levelScaled, self.level)):
            cont.blockSignals(True)
            cont.setValue(var * self.range)
            cont.blockSignals(False)

    def frame(self):
        "Convenience method"
        return self.selected['Instance'].value()

    def coil(self):
        "Convenience method"
        return self.selected['Channel'].value()

    def slice(self):
        "Convenience method"
        return self.selected['Slice'].value()

    def check_dim(self, v):
        "Disables animation checkbox for signleton dimensions"
        self.animate.setEnabled(self.stack.shape[v] > 1)

    def update_wl(self):
        """
        When only window / level have changed, we don't need to call imshow
        again, just update clim.
        """
        rng = self.window_level()
        self.image.set_clim(*rng)        
        self.canvas.draw()

    def window_input(self, value, **kwargs):
        "Handles changes in window spinbox; scales to our [0..1] range"
        self.window = value / self.range 
        self.update_wl()

    def level_input(self, value):
        "Handles changes in level spinbox; scales to our [0..1] range"
        self.level = value / self.range 
        self.update_wl()

    def mouseMoveEvent(self, event):
        "Provides window/level mouse-drag behavior."
        newx = event.x()
        newy = event.y()
        if self.mloc is None:
            self.mloc = (newx, newy)
            return 
        
        # Modify mapping and polarity as desired
        self.window = self.window - (newx - self.mloc[0]) * 0.01
        self.level = self.level - (newy - self.mloc[1]) * 0.01

        # Don't invert
        if self.window < 0:
            self.window = 0.0
        if self.window > 2:
            self.window = 2.0

        if self.level < 0:
            self.level = 0.0
        if self.level > 1:
            self.level = 1.0

        # We update the displayed (scaled by self.range) values, but
        # we don't want extra update_image calls
        for (cont, var) in ((self.windowScaled, self.window),
                            (self.levelScaled, self.level)):
            cont.blockSignals(True)
            cont.setValue(var * self.range)
            cont.blockSignals(False)

        self.mloc = (newx, newy)
        self.update_wl()

    def mouseReleaseEvent(self, event):
        "Reset .mloc to indicate we are done with one click/drag operation"
        self.mloc = None

    def wheelEvent(self, event):
        "Handle scroll event; could use some time-based limiting."
        control = self.selected['Instance']
        if event.delta() > 0:
            new_v = control.value() - 1
        elif event.delta() < 0:
            new_v = control.value() + 1
        else:
            return
        control.setValue(max(min(new_v,self.stack.shape[0]-1),0))

    def window_level(self):
        "Perform calculations of (min,max) display range from window/level"
        return (self.level * self.range 
                  - self.window / 2 * self.range + self.min, 
                self.level * self.range
                  + self.window / 2 * self.range + self.min)
    
    def update_image(self, slice_n=None):
        """
        Updates the displayed image when a set of indicies (frame/coil/slice)
        is selected. Connected to singals from the related spinboxes.
        """
        wl = self.window_level()
        self.ax.clear()
        self.image = \
            self.ax.imshow(self.stack[self.frame()][self.coil()][self.slice()], 
                           vmin=wl[0],
                           vmax=wl[1],
                           cmap=pyplot.get_cmap('gray'))
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()
        idx = self.container.images.headers[self.frame()]
        self.label.setText(self.label_base.format(int(idx['average']),int(idx['slice']),int(idx['contrast']),int(idx['phase']),int(idx['repetition']),int(idx['set'])))

    def animation(self):
        """
        Animation is achieved via a timer that drives the selected animDim
        dimensions' spinbox.
        """
        if self.animate.isChecked() is False:
            if self.timer:
                self.timer.stop()
                self.timer = None
            return
        
        dimName = self.animDim.currentText()

        if self.selected[dimName].maximum() == 0:
            logging.warn("Cannot animate singleton dimension.")
            self.animate.setChecked(False)
            return

        def increment():
            "Captures dimName"
            v = self.selected[dimName].value()
            m = self.selected[dimName].maximum()
            self.selected[dimName].setValue((v+1) % m)

        self.timer = QtCore.QTimer(self)
        self.timer.interval = 100
        self.timer.timeout.connect(increment)
        self.timer.start()

