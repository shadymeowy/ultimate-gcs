from threading import Thread
from queue import Queue
import glob
import serial
import sys
from serial.tools.list_ports import comports


import time
from .common import *


def make_dummy_connection():
    packet = Packet()

    def send_cmd(cmd):
        print(f'dummy sent {cmd}')

    queue = Queue()

    running = True

    def run():
        while running:
            packet.packet_no += 1
            packet.timestamp = int(time.time())
            packet.roll += 10
            if packet.roll > 90:
                packet.roll -= 180
            packet.pitch -= 5
            if packet.pitch < -85:
                packet.pitch += 170
            packet.yaw += 5
            if packet.yaw > 180:
                packet.yaw -= 360
            packet.horizontal_speed += 1
            packet.horizontal_acceleration += 0.3
            packet.displacement += 10
            queue.put(packet.copy())
            time.sleep(1)

    thread = Thread(target=run)
    thread.start()

    def close():
        nonlocal running
        running = False
        thread.join()

    def read_packets():
        result = []
        while not queue.empty():
            result.append(queue.get())
        return result

    return send_cmd, read_packets, close


def make_connection(name):
    port, baudrate = name.split(':')
    baudrate = int(baudrate)
    if port == 'dummy':
        return make_dummy_connection()

    ser = serial.Serial(port, baudrate, timeout=1)
    queue = Queue()

    def send_cmd(cmd):
        ser.write(cmd)

    running = True

    def run():
        while running:
            data = ser.read(52, timeout=0.1)
            if len(data) < 52:
                while ser.in_waiting > 0:
                    ser.read(ser.in_waiting)
                continue
            packet = packet_frombytes(data[:52])
            queue.put(packet)
            time.sleep(0.1)

    thread = Thread(target=run)
    thread.start()

    def close():
        nonlocal running
        running = False
        thread.join()
        ser.close()

    def read_packets():
        result = []
        while not queue.empty():
            result.append(queue.get())
        return result

    return send_cmd, read_packets, close


serial_ports = [comport.device for comport in comports()] + ['dummy']

if __name__ == '__main__':
    send_cmd, read_packets, close = make_connection('dummy')
    while True:
        packets = read_packets()
        if packets:
            print(packets)
        time.sleep(3)
