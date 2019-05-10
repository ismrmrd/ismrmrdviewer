#!/usr/bin/env python
import ui
import sys
import logging
import argparse

from PySide2 import QtWidgets

if __name__ == '__main__':

    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level='INFO'
    )

    parser = argparse.ArgumentParser(description="Simple ISMRMRD data file viewer.")
    parser.add_argument('file', type=str, nargs='?', help="ISMRMRD data file.")
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("ismrmrd-viewer")

    main = ui.MainWindow()
    main.resize(800, 600)
    main.show()

    if args.file:
        main.open_file(args.file)

    sys.exit(app.exec_())
