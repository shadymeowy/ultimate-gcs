from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from datetime import datetime

import os

if "NO_GL" not in os.environ:
    os.environ["NO_GL"] = "1"


from . import config
from .Nav2D import Nav2D
from .CustomGraph import CustomGraph
from .MapWidget import MapWidget
from .Navball import Navball
from .LogSheet import LogSheet
from .Connection import make_connection, Packet, serial_ports
from .common import *

from QPrimaryFlightDisplay import QPrimaryFlightDisplay
from functools import partial
import math
import time

DISP_U = 100
MARGIN = 0.025


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.last_row = 0
        self.last_col = 0

        self.setWindowTitle(config.APP_NAME)
        self.setWindowIcon(QIcon(config.APP_ICON))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        self.widgets = []

        self.icon = QPixmap(config.APP_ICON_LARGE)
        self.icon = self.icon.scaledToWidth(1.8 * DISP_U, Qt.SmoothTransformation)
        self.label_icon = QLabel()
        self.label_icon.setPixmap(self.icon)
        self.label_icon.setAlignment(Qt.AlignCenter)
        self.add_widget(self.label_icon, 0, 0, 2.5, 2.5)

        self.tabs = QTabWidget()
        self.map = MapWidget()
        self.tabs.addTab(self.map, 'Map')
        self.sheet = LogSheet(config.CSV_HEADERS)
        self.tabs.addTab(self.sheet, 'Log Sheet')
        self.add_widget(self.tabs, 2.5, 0, -6, None, group=False)

        self.navball = Navball()
        self.add_widget(self.navball, 0, -2.5, 2.5, None)

        graph_names = [
            ['Acceleration (m/s^2 vs s)', 'Velocity (m/s vs s)'],
            ['Displacement (m vs s)', 'Temperature (°C vs s)'],
        ]
        self.graphs = [[None, None], [None, None]]
        for x in range(2):
            for y in range(2):
                graph = CustomGraph(graph_names[y][x])
                self.graphs[y][x] = graph
                x0 = -(x * 3)
                x0 = None if x0 == 0 else x0
                y0 = y * 3
                x1 = -((x + 1) * 3)
                x1 = None if x1 == 0 else x1
                y1 = (y + 1) * 3
                self.add_widget(graph, x1, y0, x0, y1)

        self.controls_group = QGroupBox()
        self.controls_group.setLayout(QVBoxLayout())
        self.controls_connection = QGroupBox()
        self.controls_connection.setLayout(QVBoxLayout())
        self.controls_connection.layout().addWidget(QLabel('Connection'))
        self.serial_ports = QComboBox()
        self.serial_ports.addItems(serial_ports)
        self.serial_ports.setEditable(True)
        self.controls_connection.layout().addWidget(self.serial_ports)
        self.baud_rates = QComboBox()
        self.baud_rates.addItems(config.BAUD_RATES)
        self.baud_rates.setEditable(True)
        self.controls_connection.layout().addWidget(self.baud_rates)
        self.button_connect = QPushButton('Connect')
        self.button_connect.clicked.connect(self.connect_event)
        self.controls_connection.layout().addWidget(self.button_connect)
        self.button_disconnect = QPushButton('Disconnect')
        self.button_disconnect.clicked.connect(self.close_connection)
        self.controls_connection.layout().addWidget(self.button_disconnect)
        self.controls_group.layout().addWidget(self.controls_connection)
        self.controls_vehicle = QGroupBox()
        self.controls_vehicle.setLayout(QVBoxLayout())
        self.controls_vehicle.layout().addWidget(QLabel('Vehicle'))
        for cmd in config.COMMAND_NAMES:
            button = QPushButton(cmd)
            on_click = partial(self.send_cmd, cmd)
            button.clicked.connect(on_click)
            self.controls_vehicle.layout().addWidget(button)
        self.controls_group.layout().addWidget(self.controls_vehicle)
        self.controls_mode = QGroupBox()
        self.controls_mode.setLayout(QVBoxLayout())
        self.controls_mode.layout().addWidget(QPushButton('mode 1'))
        self.controls_mode.layout().addWidget(QPushButton('mode 2'))
        self.controls_group.layout().addWidget(self.controls_mode)
        self.add_widget(self.controls_group, 0, 2.5, 2.5, -2.5, group=False)

        self.pfd = QPrimaryFlightDisplay()
        self.pfd.zoom = 0.7
        self.pfd.arm = None
        self.pfd.battery = None
        self.pfd.update_style()
        self.add_widget(self.pfd, -6, 6, None, None)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_step)
        self.timer.start(1000)

    def add_widget(self, widget, x0, y0, x1, y1, group=True):
        if group:
            group = QGroupBox()
            group.setLayout(QVBoxLayout())
            group.layout().addWidget(widget)
        else:
            group = widget
        group.setParent(self)
        self.widgets.append((group, x0, y0, x1, y1))
        self.update_layout()

    def update_layout(self):
        for group, x0, y0, x1, y1 in self.widgets:
            x0 = self.normalize_x(x0) + MARGIN * DISP_U
            y0 = self.normalize_y(y0) + MARGIN * DISP_U
            x1 = self.normalize_x(x1) - MARGIN * DISP_U
            y1 = self.normalize_y(y1) - MARGIN * DISP_U
            group.setGeometry(x0, y0, x1 - x0, y1 - y0)

    def normalize_x(self, x):
        if x is None:
            return self.width()
        x *= DISP_U
        while x < 0:
            x += self.width()
        return x

    def normalize_y(self, y):
        if y is None:
            return self.height()
        y *= DISP_U
        while y < 0:
            y += self.height()
        return y

    def connect_event(self):
        serial_port = self.serial_ports.currentText()
        baud_rate = self.baud_rates.currentText()
        print(f'Connecting to {serial_port} at {baud_rate} baud')
        string = f'{serial_port}:{baud_rate}'
        try:
            self.send_cmd, self.read_packets, self.close_connection = make_connection(string)
            self.times = []
            self.accels = []
            self.vels = []
            self.disps = []
            self.temps = []
            self.start_time = int(time.time())
            self.sheet.clear()
            self.csv_file = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.csv')
            with open(self.csv_file, 'w') as f:
                f.write(','.join(config.CSV_HEADERS))
                f.write('\n')
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(str(e))
            msg.setWindowTitle('Error')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def send_cmd(self, cmd):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText('Not connected')
        msg.setWindowTitle('Error')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def read_packets(self):
        return None

    def close_connection(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText('Not connected')
        msg.setWindowTitle('Error')
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        self.update_layout()

    def timer_step(self):
        packets = self.read_packets()
        if packets is None:
            return
        for p in packets:
            self.navball.setAngle(p.pitch, p.yaw, p.roll)
            self.pfd.pitch = p.pitch * math.pi / 180
            self.pfd.roll = p.roll * math.pi / 180
            self.pfd.heading = p.yaw
            self.pfd.vspeed = p.horizontal_acceleration
            self.pfd.alt = p.displacement
            self.pfd.airspeed = p.horizontal_speed
            self.pfd.update()
            self.map.heading = p.yaw
            self.map.geo0 = (p.gps_latitude, p.gps_longitude)
            self.map.update()
            self.times.append(p.timestamp - self.start_time)
            self.accels.append(p.horizontal_acceleration)
            self.vels.append(p.horizontal_speed)
            self.disps.append(p.displacement)
            self.temps.append(p.temperature)
            graph = self.graphs[0][0]
            graph.x = self.times
            graph.y = self.accels
            graph.plot()
            graph = self.graphs[0][1]
            graph.x = self.times
            graph.y = self.vels
            graph.plot()
            graph = self.graphs[1][0]
            graph.x = self.times
            graph.y = self.disps
            graph.plot()
            graph = self.graphs[1][1]
            graph.x = self.times
            graph.y = self.temps
            graph.plot()
            entry = csv_from_packet(p).astuple()
            entry = [str(e) for e in entry]
            self.sheet.add_row(entry)
            with open(self.csv_file, 'a') as f:
                f.write(','.join(entry))
                f.write('\n')


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
