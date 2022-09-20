from datetime import datetime
from typing import Tuple, Dict

import numpy
import pandas as pandas
import pylatex
import sqlalchemy.orm
from sqlalchemy import Column, MetaData, ForeignKey, create_engine, String, func, Table
from sqlalchemy.orm import Session
from sqlalchemy.types import Integer

from pylatex import Table, MultiColumn, MultiRow
from base import Base
from devices import Device, DeviceType, get_devices, get_device_types
from feedback import Feedbackpost
from sensors import Sensor, get_sensors
from workplaces import Workplace, WorkplaceType, get_workplace_types, get_workplaces

MILLISECONDS_IN_18_HOURS = 64800000
SECONDS_IN_18_HOURS = 64800

MILLISECONDS_IN_8_HOURS = 28800000
SECONDS_IN_8_HOURS = 28800

MILLISECONDS_IN_DAY = 86400000
SECONDS_IN_DAY = 86400

DMIS_RECORDINGS_DB_PATH = "postgresql://dmis_dbuser:dmis_dbpassword@energy.uni-passau.de:6543/dmis_recordings_db"
WORKPLACE_ENUM_TABLE_NAME = "workplaceType"
SENSOR_TO_WORKPLACE_TABLE_NAME = "sensorToWorkplace"
SENSOR_TO_DEVICETYPE_TABLE_NAME = "sensorToDeviceType"


class SensorToWorkplace(Base):
    __tablename__ = SENSOR_TO_WORKPLACE_TABLE_NAME
    sensorID = Column(Integer, ForeignKey('sensor.id'), primary_key=True)
    workplaceID = Column(Integer, ForeignKey('workplace.id'), primary_key=True)


class SensorToDeviceGroup(Base):
    __tablename__ = SENSOR_TO_DEVICETYPE_TABLE_NAME
    sensorID = Column(Integer, ForeignKey('sensor_id'), primary_key=True)
    deviceTypeID = Column(Integer, ForeignKey('deviceType_id'), primary_key=True)


class SensorToDbTable(Base):
    __tablename__ = "sensorToDbTable"
    id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_table = Column(String)
    meta_table = Column(String)


metadata = MetaData()


def insert_information():
    # insert sensors
    sensor_table = Sensor.__table__
    workplace_type_table = WorkplaceType.__table__
    workplace_table = Workplace.__table__
    feedback_table = Feedbackpost.__table__
    device_type_table = DeviceType.__table__
    device_table = Device.__table__
    metadata.create_all(engine,
                        tables=[sensor_table, workplace_type_table, workplace_table, feedback_table, device_type_table,
                                device_table])
    session.add_all(get_sensors())
    session.commit()
    session.add_all(get_workplace_types())
    session.commit()
    session.add_all(get_workplaces())
    session.commit()
    session.add_all(get_device_types())
    session.commit()  # commit to avoid foreign key violation
    session.add_all(get_devices())
    session.commit()


def min_max_avg_consumption_per_device_type(measurement_table_map: Dict, device: Device, dbsession: Session,
                                            column_name: str) -> Tuple[
    float, float, float]:
    min_consumption_query = func.min(getattr(measurement_table_map[device.sensor_id]._columns, column_name))
    max_consumption_query = func.max(getattr(measurement_table_map[device.sensor_id]._columns, column_name))
    avg_consumption_query = func.avg(getattr(measurement_table_map[device.sensor_id]._columns, column_name))

    return dbsession.execute(min_consumption_query).scalar(), dbsession.execute(
        max_consumption_query).scalar(), dbsession.execute(avg_consumption_query).scalar()


def generate_idle_report(meta_table_map):
    meta_idle_report = ""
    tab = pylatex.Tabular('|l|c|c|c|c|c|')
    tab.add_hline()
    tab.add_row("Sensor", "Device", "Workplace", "Workplace Type", "Idle Time", "Idle Time in %")
    tab.add_hline()
    for sensor in session.query(Sensor).all():
        if sensor.name != "":
            meta_table = meta_table_map[sensor.id]
            # get all devices of the sensor
            devices = session.query(Device).filter(Device.sensor_id == sensor.id).all()
            for device in devices:
                # get all workplaces of the sensor
                device_type = session.query(DeviceType).filter(DeviceType.id == device.type).first()
                workplace = session.query(Workplace).filter(Workplace.id == device.workplace).first()
                workplace_type = session.query(WorkplaceType).filter(WorkplaceType.id == workplace.type).first()
                idle_time = session.query(func.count(meta_table.name).filter(meta_table.c.avg_power < 1)).scalar()
                total_time = session.query(func.count(meta_table.c.avg_power)).scalar()
                tab.add_row(f"Sensor {sensor.id}", device_type.description, workplace.id, workplace_type.description,
                            idle_time, f"{(idle_time / total_time):.2f} \%")
                tab.add_hline()

    print(tab.dumps())
    return tab.dumps()


def compute_results(metavalues=True):
    report = ""
    metareport = ""

    # map devices to sensors
    measurement_table_map = {}
    meta_table_map = {}
    for sensor in session.query(Sensor).all():
        if sensor.name != "":
            #measurement_table_map[sensor.id] = sqlalchemy.Table(sensor.name, metadata, autoload_with=engine)
            meta_table_map[sensor.id] = sqlalchemy.Table(sensor.meta_name, metadata, autoload_with=engine)

    # min, max and average consumption per device type
    # metareport, report = device_and_type_report(measurement_table_map, meta_table_map, metareport, metavalues, report)

    # min, max and average consumption per workplace type
    # metareport, report = workplace_and_type_report(measurement_table_map, meta_table_map, metareport, metavalues,
    # report)

    # min, max and average consumption per workplace on weekdays
    # metareport, report = days_and_workdays_report(measurement_table_map, meta_table_map, metareport, metavalues, report)

    idle_report = generate_idle_report(meta_table_map)

    if idle_report != "":
        with open("idle_report.tex", "w") as file:
            file.write(idle_report)
    #
    # with open("results.txt", "w") as f:
    #     f.write(report)
    # if metavalues:
    #     with open("meta_results.txt", "w") as f:
    #         f.write(metareport)


def device_and_type_report(measurement_table_map, meta_table_map, metareport, metavalues, report):
    for device_type in session.query(DeviceType).all():
        report += f"Device type: {device_type.description}\n"
        mins_per_device_type, maxs_per_device_type, avgs_per_device_type, meta_mins_per_device_type, meta_maxs_per_device_type, meta_avgs_per_device_type = (
            [] for i in range(6))
        if metavalues:
            metareport += f"Device type: {device_type.description}\n"
        for device in session.query(Device).filter(Device.type == device_type.id, Sensor.id == Device.sensor_id):
            if device.sensor_id in measurement_table_map.keys():
                min_report, max_report, avg_report = min_max_avg_consumption_per_device_type(measurement_table_map,
                                                                                             device, session,
                                                                                             "Leistung")
                mins_per_device_type.append(min_report)
                maxs_per_device_type.append(max_report)
                avgs_per_device_type.append(avg_report)
                report += f"  Device: {str(device.id)} {device_type.description}\n"
                report += f"    Min consumption: {str(min_report)}\n"
                report += f"    Max consumption: {str(max_report)}\n"
                report += f"    Avg consumption: {str(avg_report)}\n"
            if metavalues and device.sensor_id in meta_table_map.keys():
                min_meta, max_meta, avg_meta = min_max_avg_consumption_per_device_type(meta_table_map, device, session,
                                                                                       "avg_power")
                meta_mins_per_device_type.append(min_meta)
                meta_maxs_per_device_type.append(max_meta)
                meta_avgs_per_device_type.append(avg_meta)
                metareport += f"  Sensor: {str(device.id)} {device_type.description}\n"
                metareport += f"    Min consumption: {str(min_meta)}\n"
                metareport += f"    Max consumption: {str(max_meta)}\n"
                metareport += f"    Avg consumption: {str(avg_meta)}\n"
        report += f" Total min consumption: {str(min(mins_per_device_type))}\n"
        report += f" Total max consumption: {str(max(maxs_per_device_type))}\n"
        report += f" Total avg consumption: {str(sum(avgs_per_device_type) / len(avgs_per_device_type))}\n\n"
        if metavalues:
            metareport += f" Total min consumption: {str(min(meta_mins_per_device_type))}\n"
            metareport += f" Total max consumption: {str(max(meta_maxs_per_device_type))}\n"
            metareport += f" Total avg consumption: {str(sum(meta_avgs_per_device_type) / len(meta_avgs_per_device_type))}\n\n"
    return metareport, report


def workplace_and_type_report(measurement_table_map, meta_table_map, metareport, metavalues, report):
    for workplace_type in session.query(WorkplaceType).all():
        report += f"Workplace type: {workplace_type.description}\n"
        mins_per_workplace_type, maxs_per_workplace_type, avgs_per_workplace_type, meta_mins_per_workplace_type, meta_maxs_per_workplace_type, meta_avgs_per_workplace_type = (
            [] for i in range(6))
        if metavalues:
            metareport += f"Workplace type: {workplace_type.description}\n"
        for workplace in session.query(Workplace).filter(workplace_type.id == Workplace.type):
            report += f"  Workplace: {str(workplace.id)} {workplace_type.description}\n"
            mins_per_workplace, maxs_per_workplace, avgs_per_workplace, meta_mins_per_workplace, meta_maxs_per_workplace, meta_avgs_per_workplace = (
                [] for i in range(6))
            if metavalues:
                metareport += f"  Workplace: {str(workplace.id)} {workplace_type.description}\n"
            for device in session.query(Device).filter(Device.workplace == workplace.id):
                report += f"    Device: {str(device.id)} {device.description}\n"
                if device.sensor_id in measurement_table_map.keys():
                    min_report, max_report, avg_report = min_max_avg_consumption_per_device_type(measurement_table_map,
                                                                                                 device,
                                                                                                 session, "Leistung")
                    mins_per_workplace.append(min_report)
                    maxs_per_workplace.append(max_report)
                    avgs_per_workplace.append(avg_report)

                    report += f"      Min consumption: {str(min_report)}\n"
                    report += f"      Max consumption: {str(max_report)}\n"
                    report += f"      Avg consumption: {str(avg_report)}\n"
                    if metavalues and device.sensor_id in meta_table_map.keys():
                        min_meta, max_meta, avg_meta = min_max_avg_consumption_per_device_type(meta_table_map, device,
                                                                                               session, "avg_power")
                        meta_mins_per_workplace.append(min_meta)
                        meta_maxs_per_workplace.append(max_meta)
                        meta_avgs_per_workplace.append(avg_meta)
                        metareport += f"    Device: {str(device.id)} {device.description}\n"
                        metareport += f"      Min consumption: {str(min_meta)}\n"
                        metareport += f"      Max consumption: {str(max_meta)}\n"
                        metareport += f"      Avg consumption: {str(avg_meta)}\n"
            meta_workplace_min = min(mins_per_workplace)
            meta_workplace_max = max(maxs_per_workplace)
            meta_workplace_avg = sum(avgs_per_workplace) / len(avgs_per_workplace)
            report += f"   Total min consumption: {str(meta_workplace_min)}\n"
            report += f"   Total max consumption: {str(meta_workplace_max)}\n"
            report += f"   Total avg consumption: {str(meta_workplace_avg)}\n\n"
            mins_per_workplace_type.append(meta_workplace_min)
            maxs_per_workplace_type.append(meta_workplace_max)
            avgs_per_workplace_type.append(meta_workplace_avg)
            if metavalues:
                meta_workplace_min = min(meta_mins_per_workplace)
                meta_workplace_max = max(meta_maxs_per_workplace)
                meta_workplace_avg = sum(meta_avgs_per_workplace) / len(meta_avgs_per_workplace)
                metareport += f"   Total min consumption: {str(meta_workplace_min)}\n"
                metareport += f"   Total max consumption: {str(meta_workplace_max)}\n"
                metareport += f"   Total avg consumption: {str(meta_workplace_avg)}\n"
                meta_mins_per_workplace_type.append(meta_workplace_min)
                meta_maxs_per_workplace_type.append(meta_workplace_max)
                meta_avgs_per_workplace_type.append(meta_workplace_avg)
    return metareport, report


def days_and_workdays_report(measurement_table_map, meta_table_map, metareport, metavalues, report,
                             report_per_day=True):
    per_day_per_sensor_report = "sensorID;day;wholeday_avg;workday_avg\n"
    per_day_avg_values_dict, per_workday_avg_values_dict = {}, {}
    meta_result_list_whole_day, meta_result_list_work_day = [], []
    per_day_report = "day;wholeday_avg;workday_avg\n"
    bdate_start = datetime.fromisoformat('2022-06-01')
    bdate_end = datetime.now()
    pandas_weekdays = pandas.bdate_range(start=bdate_start, end=bdate_end, freq='B').astype(numpy.int64)
    report += f"Workplace consumption on weekdays from {bdate_start} until {bdate_end} or data becomes unavailable\n"
    if metavalues:
        metareport += f"Workplace consumption on weekdays from {bdate_start} until {bdate_end} or data becomes unavailable\n"
    for (sensor_id, table, meta_table) in zip(measurement_table_map.keys(), measurement_table_map.values_wholeday(),
                                              meta_table_map.values_wholeday()):
        result_list_whole_day, result_list_work_day = [], []
        for weekday_ns in pandas_weekdays:
            weekday_ms = int(weekday_ns / 1000000)
            weekday_s = int(weekday_ms / 1000)
            power_column = getattr(table._columns, "Leistung")
            timestamp_column = getattr(table._columns, "Unixtime Reply")
            whole_weekday_data = session.query(func.avg(power_column)).filter(
                timestamp_column.between(weekday_ms, weekday_ms + MILLISECONDS_IN_DAY)).scalar()
            # workday from 08:00 to 18:00
            workday_data = session.query(func.avg(power_column)).filter(
                timestamp_column.between(weekday_ms + MILLISECONDS_IN_8_HOURS,
                                         weekday_ms + MILLISECONDS_IN_18_HOURS)).scalar()
            if whole_weekday_data is not None and workday_data is not None:
                result_list_whole_day.append(whole_weekday_data)
                result_list_work_day.append(workday_data)
                if report_per_day:
                    currently_processed_day_iso = datetime.utcfromtimestamp(weekday_s).strftime('%D/%M/%Y')
                    if currently_processed_day_iso not in per_day_avg_values_dict.keys():
                        per_day_avg_values_dict[currently_processed_day_iso] = whole_weekday_data
                        per_workday_avg_values_dict[currently_processed_day_iso] = workday_data
                    else:
                        per_day_avg_values_dict[currently_processed_day_iso] += workday_data
                        per_workday_avg_values_dict[currently_processed_day_iso] += workday_data
                    per_day_per_sensor_report += f"{sensor_id};{currently_processed_day_iso};{whole_weekday_data};{workday_data}\n"
            if metavalues:
                avg_power_column = getattr(meta_table._columns, "avg_power")
                timestamp_end_column = getattr(meta_table._columns, "timestamp_end")
                whole_weekday_meta_data = session.query(func.avg(avg_power_column)).filter(
                    timestamp_end_column.between(weekday_s, weekday_s + SECONDS_IN_DAY)).scalar()
                workday_meta_data = session.query(func.avg(avg_power_column)).filter(
                    timestamp_end_column.between(weekday_s + SECONDS_IN_8_HOURS,
                                                 weekday_s + SECONDS_IN_18_HOURS)).scalar()
                if whole_weekday_meta_data is not None and workday_meta_data is not None:
                    meta_result_list_whole_day.append(whole_weekday_meta_data)
                    meta_result_list_work_day.append(workday_meta_data)
        nr_of_rec_wholedays = len(result_list_whole_day)
        wholedays_avg_value = sum(result_list_whole_day) / nr_of_rec_wholedays
        report += f"AVG consumption per weekday for Sensor{sensor_id} in {nr_of_rec_wholedays} days: {str(wholedays_avg_value)}\n"
        nr_of_rec_workdays = len(result_list_work_day)
        workdays_avg_value = sum(result_list_work_day) / nr_of_rec_workdays
        report += f"AVG consumption per workday for Sensor{sensor_id} in {nr_of_rec_workdays} workdays: {str(workdays_avg_value)}\n"
        if metavalues:
            nr_of_recorded_wholedays = len(meta_result_list_whole_day)
            wholedays_meta_avg_value = sum(meta_result_list_whole_day) / nr_of_recorded_wholedays
            metareport += f"AVG consumption per weekday for Sensor{sensor_id} in {nr_of_recorded_wholedays} days: {str(wholedays_meta_avg_value)}\n"
            nr_of_recorded_workdays = len(meta_result_list_work_day)
            workdays_meta_avg_value = sum(meta_result_list_work_day) / nr_of_recorded_workdays
            metareport += f"AVG consumption per workday for Sensor{sensor_id} in {nr_of_recorded_workdays} workdays: {str(workdays_meta_avg_value)}\n"
    if report_per_day:
        per_day_report += f"Overview of the sum of all sensors per day and workday\ndate;wholeday_avg;workday_avg\n"
        for entry in per_day_avg_values_dict.keys():
            per_day_report += f"{entry};{per_day_avg_values_dict[entry]};{per_workday_avg_values_dict[entry]}\n"
        with open('per_day_report.csv', 'w') as f:
            f.write(per_day_report)
        with open('per_day_per_sensor_report.csv', 'w') as f:
            f.write(per_day_per_sensor_report)
    return metareport, report


if __name__ == '__main__':
    engine = create_engine(
        DMIS_RECORDINGS_DB_PATH,
        echo=False)

    Session = sqlalchemy.orm.sessionmaker(bind=engine)

    session = Session()

    #insert_information()
    start = datetime.now()
    compute_results()
    end = datetime.now()
    print("Duration: " + str(end - start))
