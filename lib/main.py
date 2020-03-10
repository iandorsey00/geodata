#
# main.py
#
# The main project file.
#

from PlaceCounty import PlaceCounty

from ColumnHeader import ColumnHeader, columns

from key_hash import key_hash
import pandas as pd

# Get SQLAlchemy ready.
from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

###############################################################################
# ColumnHeaders

# Create the table
ColumnHeader.metadata.create_all(engine)

# Place data into DataFrame
column_headers_df = pd.read_csv('../data/ACS_5yr_Seq_Table_Number_Lookup.txt',
    dtype='str')

# Declare a list to store column headers
column_headers = []

for index, data in column_headers_df.iterrows():
    # Create column header models
    ch = ColumnHeader()

    for idx, column in enumerate(columns):
        # Dynamically assign data to each attribute
        setattr(ch, column, data[idx])
    
    column_headers.append(ch)

for column_header in column_headers:
    # Add column headers to database
    session.add(column_header)

###############################################################################
# Places

# Get the county given a name string from summary level 155.
def get_county(sl_155_geo_name_string):
    # Split the name string by ", "
    split_geo_name_string = sl_155_geo_name_string.split(", ")
    # Get the first part, which will be of format XXX County (part)
    county_part = split_geo_name_string[0]
    # Return only the part before " (part)"
    return county_part[:-7]

def get_place(sl_155_geo_name_string):
    # Split the name string by ", "
    split_geo_name_string = sl_155_geo_name_string.split(", ")
    return ", ".join(split_geo_name_string[1:])

# Create the table
PlaceCounty.metadata.create_all(engine)

# First, put all places into a pandas DataFrame.
places_df = pd.read_csv('../data/g20185ca.csv', encoding='iso-8859-1', \
dtype='str', header=0)
# Filter for rows where the summary level is 155.
places_df = places_df.loc[places_df.iloc[:,2] == '155']

# Declare an array to hold instances of PlaceCounty.
places = []

# Get population data.
pop_df = pd.read_csv('../data/e20185ca0002000.txt', dtype='str', header=None)

# Iterate through the DataFrame and convert each row to a Place model.
for index, data in places_df.iterrows():
    # Assign our data to temporary variables.

    # LOGRECNO matches a geo entry with its data.
    _logrecno = data[4]
    _state = 'California'
    _name = get_place(data[49])
    _key = key_hash(_name)
    _county = get_county(data[49])
    # For now, look up the population using pandas.
    # Create the models.
    places.append(PlaceCounty(logrecno=_logrecno, key=_key, state=_state, \
    county=_county, name=_name))

# Add the places to our SQLite database.
for place in places:
    session.add(place)

# Commit changes
session.commit()

# Print the first five column headers for debugging purposes.
for instance in session.query(ColumnHeader).limit(5):
    print(instance)

# Print the five largest places in California for debugging purposes.
for instance in session.query(PlaceCounty).limit(5):
    print(instance)
