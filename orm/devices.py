from base import Base
from sqlalchemy.types import String, Integer
from sqlalchemy import Column, ForeignKey


PC, MONITOR, UTILITY, PRINTER, MULTIPLE = range(5)

class DeviceType(Base):
    __tablename__ = "deviceType"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)


class Device(Base):
    __tablename__ = "device"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)
    type = Column(Integer, ForeignKey('deviceType.id'))
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    workplace = Column(Integer, ForeignKey("workplace.id"))

def get_device_types():
    return [
        DeviceType(id=PC, description="PC"),
        DeviceType(id=MONITOR, description="Monitor"),
        DeviceType(id=UTILITY, description="Utility"),
        DeviceType(id=PRINTER, description="Printer"),
        DeviceType(id=MULTIPLE, description="Multiple")
    ]


def get_devices():
    return [
    Device(id=1, description="PC",type=PC, sensor_id=1, workplace=0),
    Device(id=2, description="PC",type=MONITOR, sensor_id=2, workplace=0),
    Device(id=3, description="PC",type=MONITOR, sensor_id=3, workplace=0),
    Device(id=4, description="PC",type=PC, sensor_id=4, workplace=1),
    Device(id=5, description="PC",type=MONITOR, sensor_id=5, workplace=1),
    Device(id=6, description="PC",type=MONITOR, sensor_id=6, workplace=1),
    Device(id=7, description="PC",type=PC, sensor_id=7, workplace=1),
    Device(id=8, description="PC",type=MONITOR, sensor_id=8, workplace=1),
    Device(id=9, description="PC",type=MONITOR, sensor_id=9, workplace=1),
    Device(id=10, description="PC",type=PC, sensor_id=10, workplace=2),
    Device(id=11, description="PC",type=MONITOR, sensor_id=11, workplace=2),
    Device(id=12, description="PC",type=PRINTER, sensor_id=12, workplace=2),
    Device(id=13, description="PC",type=UTILITY, sensor_id=13, workplace=2),
    Device(id=14, description="PC",type=PC, sensor_id=14, workplace=3),
    Device(id=15, description="PC",type=MONITOR, sensor_id=15, workplace=3),
    Device(id=16, description="PC",type=PC, sensor_id=16, workplace=3),
    Device(id=17, description="PC",type=MONITOR, sensor_id=17, workplace=3),
    Device(id=18, description="PC",type=MONITOR, sensor_id=18, workplace=3),
    Device(id=19, description="PC",type=PC, sensor_id=19, workplace=3),
    Device(id=20, description="PC",type=MONITOR, sensor_id=20, workplace=3),
    Device(id=21, description="PC",type=MONITOR, sensor_id=21, workplace=3),
    Device(id=22, description="PC",type=PRINTER, sensor_id=22, workplace=3),
    Device(id=23, description="PC",type=PC, sensor_id=23, workplace=4),
    Device(id=24, description="PC",type=MONITOR, sensor_id=24, workplace=4),
    Device(id=25, description="PC",type=MONITOR, sensor_id=25, workplace=4),
    Device(id=26, description="PC",type=PC, sensor_id=26, workplace=4),
    Device(id=27, description="PC",type=MONITOR, sensor_id=27, workplace=4),
    Device(id=28, description="PC",type=MONITOR, sensor_id=28, workplace=4),
    Device(id=29, description="PC",type=MONITOR, sensor_id=29, workplace=4),
    Device(id=30, description="PC",type=PC, sensor_id=30, workplace=4),
    Device(id=31, description="PC",type=MONITOR, sensor_id=31, workplace=4),
    Device(id=32, description="PC",type=UTILITY, sensor_id=32),
    Device(id=33, description="PC",type=MULTIPLE, sensor_id=33, workplace=5),
    Device(id=34, description="PC",type=MULTIPLE, sensor_id=34, workplace=6),
    Device(id=35, description="PC",type=MULTIPLE, sensor_id=35, workplace=6),
    Device(id=36, description="PC",type=MULTIPLE, sensor_id=36, workplace=7),
    Device(id=37, description="PC",type=MULTIPLE, sensor_id=37, workplace=7)
]