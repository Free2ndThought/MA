import datetime
import time

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, func
import inspect

DMIS_RECORDINGS_DB = 'postgresql://dmis_dbuser:dmis_dbpassword@dmis_db-container/dmis_recordings_db'


def retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var][0]


Base = automap_base()

# engine, suppose it has two tables 'user' and 'address' set up

new_adress = DMIS_RECORDINGS_DB.replace('dmis_db-container', 'energy.uni-passau.de:6543')

engine = create_engine(new_adress)

# reflect the tables
Base.prepare(engine, reflect=True)


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
