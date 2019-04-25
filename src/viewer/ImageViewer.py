import logging

from PySide2 import QtWidgets


class ImageViewer(QtWidgets.QWidget):

    def __init__(self, container):
        super().__init__()

        self.container = container

        logging.info("Image constructor.")
