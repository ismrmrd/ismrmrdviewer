
import logging

from PySide2 import QtWidgets


class HeaderViewer(QtWidgets.QPlainTextEdit):

    def __init__(self, container):
        super().__init__()

        self.container = container

        self.setReadOnly(True)
        self.setTabChangesFocus(True)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        dom = container.header.toDOM()
        xml = dom.toprettyxml(indent=4*' ')

        self.setPlainText(xml)


