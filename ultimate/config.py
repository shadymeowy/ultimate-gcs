APP_NAME = 'Ultimate Thingy'
import pkg_resources
ASSETS = 'assets'
APP_ICON = pkg_resources.resource_filename(ASSETS, 'icon.ico')
APP_ICON_LARGE = pkg_resources.resource_filename(ASSETS, 'icon.png')
CURSOR_MASK = pkg_resources.resource_filename(ASSETS, 'cursor_mask.png')
NAVBALL_MASK = pkg_resources.resource_filename(ASSETS, 'navball_mask.png')

CSV_HEADERS_TR = [
    "Takım No",
    "Yıl",
    "Ay",
    "Gün",
    "Saat",
    "Dakika",
    "Saniye",
    "Yatay Hız (m/s)",
    "Yatay İvme (m/s^2)",
    "GPS Enlem (degree)",
    "GPS Boylam (degree)",
    "GPS Yükseklik (m)",
    "Yer Değiştirme (m)",
    "Pitch (degree)",
    "Roll (degree)",
    "Yaw (degree)",
    "Pil Gerilimi (V)",
    "Paket Doğruluğu",
]

CSV_HEADERS = [
    "Team No",
    "Packet No",
    "Year",
    "Month",
    "Day",
    "Hour",
    "Minute",
    "Second",
    "Horizontal Speed (m/s)",
    "Horizontal Acceleration (m/s^2)",
    "GPS Latitude (degree)",
    "GPS Longitude (degree)",
    "GPS Altitude (m)",
    "Displacement (m)",
    "Pitch (degree)",
    "Roll (degree)",
    "Yaw (degree)",
    "Battery Voltage (V)",
    "Packet Integrity",
]

BAUD_RATES = ['4800', '9600', '19200', '38400', '57600', '115200']
COMMAND_NAMES_TR = ['Eve Dön', 'Görüntü Al', 'Hızlan']
COMMAND_NAMES = ['Return to home', 'Take picture', 'Accelerate']
COMMAND_VALUES = [1, 2, 3]
COMMANDS = dict(zip(COMMAND_NAMES, COMMAND_VALUES))