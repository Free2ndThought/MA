from sqlalchemy.types import String, Integer
from sqlalchemy import Column
from base import Base

class Feedbackpost(Base):
    __tablename__ = "feedbackpost"
    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback = Column(String)
    user = Column(String)
    timestamp = Column(String)
    def __init__(self, feedback, user, timestamp):
        self.feedback = feedback
        self.user = user
        self.timestamp = timestamp
    def __repr__(self):
        return "<Feedbackpost(feedback='%s', user='%s', timestamp='%s')>" % (self.feedback, self.user, self.timestamp)