# 
# PlaceCounty.py
#
# Stores information for places within counties.
#
# PlaceCounty should be used (as opposed to Places) when places in a state
# don't typically cross county lines.
#
# The U.S. Census Bureau summary level code for PlaceCounties is 155.
#

# declarative_base() is the class which all models inherit.
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Index

class PlaceCounty(Base):
    __tablename__ = 'place_counties'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    state = Column(String)
    county = Column(String)
    name = Column(String)

    def __repr__(self):
            return "<PlaceCounty(key='%s', state='%s', county='%s', name='%s')>" % (
                self.key, self.state, self.county, self.name)
