from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class LogSheet(QWidget):
    def __init__(self, header):
        super(LogSheet, self).__init__()
        self.table = QTableWidget(self)
        self.table.setColumnCount(len(header))
        self.table.setHorizontalHeaderLabels(header)
        for i in range(len(header)):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.resizeEvent(None)

    def add_row(self, row):
        self.table.setRowCount(self.table.rowCount() + 1)
        for i, item in enumerate(row):
            item = QTableWidgetItem()
            self.table.setItem(self.table.rowCount() - 1, i, item)
            item.setText(row[i])
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.table.scrollToBottom()

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def resizeEvent(self, event):
        self.table.resize(self.size())

    def clear(self):
        self.table.clearContents()
        self.table.setRowCount(0)


if __name__ == '__main__':
    app = QApplication([])
    window = LogSheet(['a', 'b', 'c'])
    window.add_rows([['1', '2', '3'], ['4', '5', '6']])
    for i in range(100):
        window.add_row([str(i), str(i), str(i)])
    window.show()
    app.exec()
