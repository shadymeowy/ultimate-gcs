from dataclasses import dataclass, astuple, replace
from datetime import datetime
from struct import pack, unpack
from crcmod import mkCrcFun

struct_fmt = '=' + 'HHI' + 'ff' + 'ffi' + 'f' + 'fff' + 'ff' + 'H'


@dataclass
class CSVEntry:
    team_no: int
    packet_no: int
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    horizontal_speed: float
    horizontal_acceleration: float
    gps_latitude: float
    gps_longitude: float
    gps_altitude: int
    displacement: float
    pitch: float
    roll: float
    yaw: float
    battery_voltage: float
    packet_integrity: int

    def astuple(self):
        return astuple(self)

    def copy(self, **kwargs):
        return replace(self, **kwargs)


@dataclass
class Packet:
    team_no: int = 101
    packet_no: int = 0
    timestamp: int = 0
    horizontal_speed: float = 0
    horizontal_acceleration: float = 0
    gps_latitude: float = 39.89093263
    gps_longitude: float = 32.7826995
    gps_altitude: int = 916
    displacement: float = 0
    pitch: float = 0
    roll: float = 0
    yaw: float = 0
    battery_voltage: float = 7.5
    temperature: float = 20
    crc16: int = 0xdead

    def copy(self, **kwargs):
        return replace(self, **kwargs)


def csv_from_packet(packet):
    t = datetime.fromtimestamp(packet.timestamp)
    return CSVEntry(
        team_no=packet.team_no,
        packet_no=packet.packet_no,
        year=t.year,
        month=t.month,
        day=t.day,
        hour=t.hour,
        minute=t.minute,
        second=t.second,
        horizontal_speed=packet.horizontal_speed,
        horizontal_acceleration=packet.horizontal_acceleration,
        gps_latitude=packet.gps_latitude,
        gps_longitude=packet.gps_longitude,
        gps_altitude=packet.gps_altitude,
        displacement=packet.displacement,
        pitch=packet.pitch,
        roll=packet.roll,
        yaw=packet.yaw,
        battery_voltage=packet.battery_voltage,
        packet_integrity=1 if check_packet(packet) else 0,
    )


def packet_frombytes(bytes):
    result = unpack(struct_fmt, bytes)
    return Packet(
        team_no=result[0],
        packet_no=result[1],
        timestamp=result[2],
        horizontal_speed=result[3],
        horizontal_acceleration=result[4],
        gps_latitude=result[5],
        gps_longitude=result[6],
        gps_altitude=result[7],
        displacement=result[8],
        pitch=result[9],
        roll=result[10],
        yaw=result[11],
        battery_voltage=result[12],
        temperature=result[13],
        crc16=result[14],
    )


def packet_tobytes(packet):
    return pack(struct_fmt,
                packet.team_no,
                packet.packet_no,
                packet.timestamp,
                packet.horizontal_speed,
                packet.horizontal_acceleration,
                packet.gps_latitude,
                packet.gps_longitude,
                packet.gps_altitude,
                packet.displacement,
                packet.pitch,
                packet.roll,
                packet.yaw,
                packet.battery_voltage,
                packet.temperature,
                packet.crc16,
                )


def crc16ibm(data):
    fun = mkCrcFun(0x18005, initCrc=0x0000, rev=True, xorOut=0x0000)
    return fun(data)


def check_integrity(bb):
    return crc16ibm(bb) == bb[-2:]


def update_crc(packet):
    packet.crc16 = crc16ibm(packet_tobytes(packet)[:-2])


def check_packet(packet):
    return packet.crc16 == crc16ibm(packet_tobytes(packet)[:-2])


if __name__ == '__main__':
    packet = Packet()
    print(packet)
    print(check_packet(packet))
    print(csv_from_packet(packet))
    update_crc(packet)
    print(packet)
    print(check_packet(packet))
    print(csv_from_packet(packet))
