# 
# Place.py
#
# This class will store all the information regarding a place.
#

# declarative_base() is the class which all models inherit.
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String

class Place(Base):
    __tablename__ = 'place'

    id = Column(String, primary_key=True)
    key = Column(String)
    name = Column(String)
    pop = Column(Integer)

    def __repr__(self):
            return "<Place(key='%s', name='%s', pop=%s)>" % (
                self.key, self.name, self.pop)
