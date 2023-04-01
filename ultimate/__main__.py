import sys
from PySide6.QtWidgets import *


from .MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    r = app.exec()
    sys.exit(r)


if __name__ == "__main__":
    main()
