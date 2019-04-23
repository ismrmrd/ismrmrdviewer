
import ui
import sys

from PySide2 import QtWidgets


def open_file(file_name):
    print("Opening file: " + file_name)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = ui.MainWindow()
    main.resize(800, 600)
    main.show()

    main.open.connect(open_file)

    sys.exit(app.exec_())
