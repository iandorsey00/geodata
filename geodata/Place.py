# 
# Place.py
#
# This class will store all the information regarding a place.
#

from initialize_sqlalchemy import Base
from sqlalchemy import Column, Integer, String, Index

class Place(Base):
    __tablename__ = 'place'

    id = Column(Integer, primary_key=True)
    logrecno = Column(String)
    key = Column(String)
    state = Column(String)
    name = Column(String)

    def __repr__(self):
            return "<PlaceCounty(key='%s', state='%s', name='%s'>" % (
                self.key, self.state, self.name)
