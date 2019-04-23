
import ui
import sys
import logging

from PySide2 import QtWidgets


if __name__ == '__main__':

    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level='INFO'
    )

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("ismrmrd-viewer")

    main = ui.MainWindow()
    main.resize(800, 600)
    main.show()

    sys.exit(app.exec_())
