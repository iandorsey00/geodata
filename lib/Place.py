# 
# Place.py
#
# This class will store all the information regarding a place.
#

# declarative_base() is the class which all models inherit.
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Index

class Place(Base):
    __tablename__ = 'place'

    id = Column(Integer, primary_key=True)
    geo_id = Column(String)
    key = Column(String)
    name = Column(String)
    county = Column(String)
    pop = Column(Integer)

    Index('idx_geo_id', geo_id, unique=True)

    def __repr__(self):
            return "<Place(geo_id='%s', key='%s', name='%s', county='%s' " + \
            "pop=%s)>" % (
                self.geo_id, self.key, self.name, self.pop)
