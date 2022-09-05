import datetime
import time

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, func
from consumer.pika_consumer import DMIS_RECORDINGS_DB

import inspect


def retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var][0]


Base = automap_base()

# engine, suppose it has two tables 'user' and 'address' set up

new_adress = DMIS_RECORDINGS_DB.replace('dmis_db-container', 'energy.uni-passau.de:6543')

engine = create_engine(new_adress)

# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name.
# Sensor_1 = Base.classes.BLADL_00_001
# Sensor_2 = Base.classes.BLADL_00_002
# Sensor_3 = Base.classes.BLADL_00_003
# Sensor_4 = Base.classes.BLADL_00_004
# Sensor_5 = Base.classes.BLADL_00_005
# Sensor_6 = Base.classes.BLADL_00_006
# Sensor_7 = Base.classes.BLADL_00_007
# Sensor_8 = Base.classes.BLADL_00_008
# Sensor_9 = Base.classes.BLADL_00_009
# Sensor_10 = Base.classes.BLADL_00_010
# Sensor_11 = Base.classes.BLADL_00_011
# Sensor_12 = Base.classes.BLADL_00_012
# Sensor_13 = Base.classes.BLADL_00_013
# Sensor_14 = Base.classes.BLADL_00_014
# Sensor_15 = Base.classes.BLADL_00_015
# Sensor_16 = Base.classes.BLADL_00_016
# Sensor_17 = Base.classes.BLADL_00_017
# Sensor_18 = Base.classes.BLADL_00_018
# Sensor_19 = Base.classes.BLADL_00_019
# Sensor_20 = Base.classes.BLADL_00_020
# Sensor_21 = Base.classes.BLADL_00_021
# Sensor_22 = Base.classes.BLADL_00_022
# Sensor_23 = Base.classes.BLADL_00_023
# Sensor_24 = Base.classes.BLADL_00_024
# Sensor_25 = Base.classes.BLADL_00_025
# Sensor_26 = Base.classes.BLADL_00_026
# Sensor_27 = Base.classes.BLADL_00_027
# Sensor_28 = Base.classes.BLADL_00_028
# Sensor_29 = Base.classes.BLADL_00_029
# Sensor_30 = Base.classes.BLADL_00_030
# Sensor_31 = Base.classes.BLADL_00_031
# Sensor_32 = Base.classes.BLADL_00_032
# Sensor_33 = Base.classes.BLADL_00_033
# Sensor_34 = Base.classes.BLADL_00_034
# Sensor_35 = Base.classes.BLADL_00_035
# Sensor_36 = Base.classes.BLADL_00_036
# Sensor_37 = Base.classes.BLADL_00_037
# sensorList = [Sensor_1, Sensor_2, Sensor_3, Sensor_3, Sensor_4, Sensor_5, Sensor_6, Sensor_7, Sensor_8, Sensor_9,
#               Sensor_10, Sensor_11, Sensor_12, Sensor_13, Sensor_14, Sensor_15, Sensor_16, Sensor_17, Sensor_18,
#               Sensor_19,
#               Sensor_20, Sensor_21, Sensor_22, Sensor_23, Sensor_24, Sensor_25, Sensor_26, Sensor_27, Sensor_28,
#               Sensor_29,
#               Sensor_30, Sensor_31, Sensor_32, Sensor_33, Sensor_34, Sensor_35, Sensor_36, Sensor_37]

def sensor_generator():
    metadata_object = sqlalchemy.MetaData()
    metadata_object.reflect(bind=engine)
    i = 1
    for table in metadata_object.sorted_tables:
        yield table, i, metadata_object
        i += 1

def interval_end_generator(session: Session, table: sqlalchemy.table, interval_length: int, **kwargs):
    interval_column = getattr(table._columns, 'Unixtime Reply')
    interval_begin = kwargs.get('interval_begin', None)
    interval_termination = kwargs.get('interval_termination', time.time() * 1000)
    if interval_begin is None:
        interval_begin = session.execute(select(func.min(interval_column))).first()[0]
    value_in_db = session.execute(select(interval_column).where(interval_column >= interval_begin).limit(1)).all()
    while value_in_db.__len__() > 0 and interval_begin < interval_termination:
        interval_end = interval_begin + interval_length
        yield interval_begin, interval_end, datetime.datetime.fromtimestamp(interval_begin)
        interval_begin = interval_end
        value_in_db = session.execute(select(interval_column).where(interval_column >= interval_begin).limit(1)).all()


def compute_average_power(session: Session, table: sqlalchemy.table, interval_begin: int, interval_end: int):
    interval_column = getattr(table._columns, 'Unixtime Reply')
    power_column = getattr(table._columns, 'Leistung')
    stmnt = select(func.avg(power_column), func.count(power_column)).filter(interval_column >= interval_begin * 1000).filter(interval_column < interval_end * 1000)
    q_result = session.execute(stmnt)
    return_tuple = q_result.first()
    return return_tuple[0], return_tuple[1]


def create_table_and_insert_values(session: Session, metadata: sqlalchemy.MetaData, table_name: str, values: list):

    if not sqlalchemy.inspect(engine).has_table(f'{table_name}'):
        meta_table = sqlalchemy.Table(f'{table_name}', Base.metadata,
                                      sqlalchemy.Column('timestamp_end', sqlalchemy.Integer, primary_key=True,
                                                        autoincrement=False),
                                      sqlalchemy.Column('avg_power', sqlalchemy.Float, nullable=True),
                                      sqlalchemy.Column('measurement_count', sqlalchemy.Integer, nullable=True))
        meta_table.create(bind=engine)
        metadata_object._add_table(meta_table.name,None, meta_table)
        print(f'table {meta_table.name} created')
    else:
        meta_table = metadata.tables[f'{table_name}']
        print(f'table already exists')
    print('Inserting values ...')
    session.execute(meta_table.insert(), values)
    print('Insert finished')


start_time = datetime.datetime.now()
print(start_time)
session = Session(engine)


def determine_if_table_finished(i: int, metadata_object: sqlalchemy.MetaData):
    table_name = f"Sensor_{i}_meta"
    meta_table = metadata_object.tables.get(f'{table_name}')
    if meta_table is None:
        return False
    qvalue = session.query(meta_table).first()

    if qvalue is None:
        return False
    else:
        return True


for sensor_table, i, metadata_object in sensor_generator():
    if "meta" in sensor_table.name:
        print("meta tables reached, terminating process ...")
        break
    sensor_starttime = datetime.datetime.now()
    if determine_if_table_finished(i, metadata_object):
        print(f'table Sensor{i} is finished, skipping ...')
        continue
    average_power_dict_list = []  # [{timestamp_end: INT , avg_power: INT} ...]
    insert_flush_iterator = 0
    for interval_timestamp_begin, interval_timestamp_end, interval_datetime in interval_end_generator(session, sensor_table,
                                                                                                      900,
                                                                                                      interval_begin=1651356000,
                                                                                                      interval_termination=1656626400):
        average_power, measurement_count = compute_average_power(session, sensor_table, interval_timestamp_begin, interval_timestamp_end)
        average_power_dict_list.append({'timestamp_end': interval_timestamp_end, 'avg_power': average_power,
                                        'measurement_count': measurement_count})
        if insert_flush_iterator >= 999:
            create_table_and_insert_values(session, metadata_object, f'Sensor_{i}_meta', average_power_dict_list)
            average_power_dict_list = []
            insert_flush_iterator = 0
        else:
            insert_flush_iterator += 1

    create_table_and_insert_values(session, metadata_object, f'Sensor_{i}_meta', average_power_dict_list)
    end_time = datetime.datetime.now()
    print(f'table Sensor_{i} completion time: {end_time - sensor_starttime}')
    session.commit()

end_time = datetime.datetime.now()
print(f'completion time: {end_time - start_time}')
