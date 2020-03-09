#
# main.py
#
# The main project file.
#

from PlaceCounty import PlaceCounty
from key_hash import key_hash
import pandas as pd

# Get SQLAlchemy ready.
from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

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

places = []

# Iterate through the DataFrame and convert each row to a Place model.
for index, data in places_df.iterrows():
    # Assign our data to temporary variables.
    _state = 'California'
    _name = get_place(data[49])
    _key = key_hash(_name)
    _county = get_county(data[49])
    # Create the models.
    places.append(PlaceCounty(key=_key, state=_state, county=_county, \
    name=_name))

# Add the places to our SQLite database.
for place in places:
    session.add(place)

# Commit changes
session.commit()

# Print the five largest places in California for debugging purposes.
for instance in session.query(PlaceCounty).limit(5):
    print(instance)
