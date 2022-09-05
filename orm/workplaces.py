from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer
from sqlalchemy import ForeignKey
from sqlalchemy import Column
from base import Base


class WorkplaceType(Base):
    __tablename__ = 'workplaceType'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)

class Workplace(Base):
    __tablename__ = 'workplace'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Integer, ForeignKey('workplaceType.id'))


def get_workplace_types():
    return [
    WorkplaceType(id=0, description="Single"),
    WorkplaceType(id=1, description="Dual"),
    WorkplaceType(id=2, description="Multi")
]

def get_workplaces():
    return [
    Workplace(id=0, type=0), # Sensor 1-3
    Workplace(id=1, type=1), # Sensor 4-9
    Workplace(id=2, type=0), # Sensor 10-13
    Workplace(id=3, type=0), # Sensor 14
    Workplace(id=4, type=2), # Sensor 15 -23
    Workplace(id=5, type=2), # Sensor 24 - 32
    Workplace(id=6, type=1), # Sensor 34 - 37
    Workplace(id=7, type=1) # Sensor 38 - 39
]
