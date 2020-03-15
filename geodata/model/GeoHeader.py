# 
# GeoHeaders.py
#
# Store geographical data about geographies.
#

import pandas as pd
from initialize_sqlalchemy import Base
from sqlalchemy import Column, Integer, String, Index, ForeignKey
from sqlalchemy.orm import relationship

def create_geoheader_class(path):
    # Obtain column headers for the column headers
    columns = list(pd.read_csv(path + '2019_Gaz_place_national.txt',
        sep='\t', nrows=1, dtype='str').columns)

    # Dynamic table creation: Create an attr_dict to store table attributes
    attr_dict = {}

    # Set the name for the table.
    attr_dict['__tablename__'] = 'geo_headers'

    # Define the class's __repr__
    def _repr(self):
        return "<GeoHeader(USPS='%s', GEOID='%s', NAME='%s', ALAND_SQMI='%s' ...)>" % (
            self.USPS, self.GEOID, self.NAME, self.ALAND_SQMI)

    # Add the definition above to the class
    attr_dict['__repr__'] = _repr

    for column in columns:
        if column == 'GEOID':
            # Set GEOID as the primary key
            attr_dict[column] = Column(String, \
                ForeignKey('place_counties.geo_id'), primary_key=True)
        else:
            attr_dict[column] = Column(String)

    # Add the relationship
    attr_dict['placecounty'] = relationship('PlaceCounty', \
        back_populates='geoheader')

    # Dynamically create ColumnHeader class using attr_dict
    return type('GeoHeader', (Base,), attr_dict)
