# 
# ColumnHeader.py
#
# Store information about column headers. This class will be dynamically
# created because it has lots of columns.
#

import pandas as pd
# from initialize_sqlalchemy import Base
# from sqlalchemy import Column, Integer, String, Index

def get_ch_columns(path):
    '''Obtain columns for table_metadata'''
    columns = list(pd.read_csv(path + 'ACS_5yr_Seq_Table_Number_Lookup.csv',
        nrows=1, dtype='str').columns)

    # Convert column headers to snake_case
    columns = list(map(lambda x: x.lower(), columns))
    columns = list(map(lambda x: x.replace(' ', '_'), columns))

    return columns

# Old code
# def create_ch_class(path):
#     '''Dynamically create the ColumnHeader class'''
#     columns = get_ch_columns(path)

#     # Dynamic table creation: Create an attr_dict to store table attributes
#     attr_dict = {}

#     # Set the name for the table.
#     attr_dict['__tablename__'] = 'column_headers'

#     # Give the table an id column
#     attr_dict['id'] = Column(Integer, primary_key=True)

#     # Define the class's __repr__
#     def _repr(self):
#         return "<ColumnHeader(table_id='%s', sequence_number='%s', line_number='%s', start_position='%s', table_title='%s' ...)>" % (
#             self.table_id, self.sequence_number, self.line_number,
#             self.start_position, self.table_title)

#     # Add the definition above to the class
#     attr_dict['__repr__'] = _repr

#     for column in columns:
#         # Set the 'table_id' column to be the primary key.
#         attr_dict[column] = Column(String)

#     # Dynamically create ColumnHeader class using attr_dict
#     return type('ColumnHeader', (Base,), attr_dict)
