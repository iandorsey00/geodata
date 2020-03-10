# 
# ColumnHeader.py
#
# Store information about column headers. This class will be dynamically
# created because it has lots of columns.
#

import pandas as pd

# Obtain column headers for the column headers
columns = list(pd.read_csv('../data/ACS_5yr_Seq_Table_Number_Lookup.txt',
    nrows=1, dtype='str').columns)

# Convert column headers to snake_case
columns = list(map(lambda x: x.lower(), columns))
columns = list(map(lambda x: x.replace(' ', '_'), columns))

# declarative_base() is the class which all models inherit.
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Index

# Dynamic table creation: Create an attr_dict to store table attributes
attr_dict = {}

# Set the name for the table.
attr_dict['__tablename__'] = 'column_headers'

# Give the table an id column
attr_dict['id'] = Column(Integer, primary_key=True)

# Define the class's __repr__
def _repr(self):
    return "<ColumnHeader(table_title='%s' ...)>" % (self.table_title)

# Add the definition above to the class
attr_dict['__repr__'] = _repr

for column in columns:
    # Set the 'table_id' column to be the primary key.
    attr_dict[column] = Column(String)

# Dynamically create ColumnHeader class using attr_dict
ColumnHeader = type('ColumnHeader', (Base,), attr_dict)
