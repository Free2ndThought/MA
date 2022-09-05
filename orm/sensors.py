from base import Base
from sqlalchemy.types import String, Integer
from sqlalchemy import Column


class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    meta_name = Column(String)

def get_sensors():
    return [
    Sensor(id=1, name="BLADL_00_001", meta_name="Sensor_1_meta"),
    Sensor(id=2, name="BLADL_00_002", meta_name="Sensor_2_meta"),
    Sensor(id=3, name="BLADL_00_003", meta_name="Sensor_3_meta"),
    Sensor(id=4, name="BLADL_00_004", meta_name="Sensor_4_meta"),
    Sensor(id=5, name="BLADL_00_005", meta_name="Sensor_5_meta"),
    Sensor(id=6, name="BLADL_00_006", meta_name="Sensor_6_meta"),
    Sensor(id=7, name="BLADL_00_007", meta_name="Sensor_7_meta"),
    Sensor(id=8, name="BLADL_00_008", meta_name="Sensor_8_meta"),
    Sensor(id=9, name="BLADL_00_009", meta_name="Sensor_9_meta"),
    Sensor(id=10, name="BLADL_00_010", meta_name="Sensor_10_meta"),
    Sensor(id=11, name="BLADL_00_011", meta_name="Sensor_11_meta"),
    Sensor(id=12, name="BLADL_00_012", meta_name="Sensor_12_meta"),
    Sensor(id=13, name="BLADL_00_013", meta_name="Sensor_13_meta"),
    Sensor(id=14, name="BLADL_00_014", meta_name="Sensor_14_meta"),
    Sensor(id=15, name="BLADL_00_015", meta_name="Sensor_15_meta"),
    Sensor(id=16, name="BLADL_00_016", meta_name="Sensor_16_meta"),
    Sensor(id=17, name="BLADL_00_017", meta_name="Sensor_17_meta"),
    Sensor(id=18, name="BLADL_00_018", meta_name="Sensor_18_meta"),
    Sensor(id=19, name="BLADL_00_019", meta_name="Sensor_19_meta"),
    Sensor(id=20, name="BLADL_00_020", meta_name="Sensor_20_meta"),
    Sensor(id=21, name="BLADL_00_021", meta_name="Sensor_21_meta"),
    Sensor(id=22, name="BLADL_00_022", meta_name="Sensor_22_meta"),
    Sensor(id=23, name="BLADL_00_023", meta_name="Sensor_23_meta"),
    Sensor(id=24, name="BLADL_00_024", meta_name="Sensor_24_meta"),
    Sensor(id=25, name="BLADL_00_025", meta_name="Sensor_25_meta"),
    Sensor(id=26, name="BLADL_00_026", meta_name="Sensor_26_meta"),
    Sensor(id=27, name="BLADL_00_027", meta_name="Sensor_27_meta"),
    Sensor(id=28, name="BLADL_00_028", meta_name="Sensor_28_meta"),
    Sensor(id=29, name="BLADL_00_029", meta_name="Sensor_29_meta"),
    Sensor(id=30, name="BLADL_00_030", meta_name="Sensor_30_meta"),
    Sensor(id=31, name="BLADL_00_031", meta_name="Sensor_31_meta"),
    Sensor(id=32, name="BLADL_00_032", meta_name="Sensor_32_meta"),
    Sensor(id=33, name="BLADL_00_033", meta_name="Sensor_33_meta"),
    Sensor(id=34, name="BLADL_00_034", meta_name="Sensor_34_meta"),
    Sensor(id=35, name="BLADL_00_035", meta_name="Sensor_35_meta"),
    Sensor(id=36, name="BLADL_00_036", meta_name="Sensor_36_meta"),
    Sensor(id=37, name="BLADL_00_037", meta_name="Sensor_37_meta")
]
