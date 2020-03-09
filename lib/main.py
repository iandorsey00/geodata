#
# main.py
#
# The main project file.
#

from Place import Place
from key_hash import key_hash
import pandas as pd

# Get SQLAlchemy ready.
from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# Create the table
Place.metadata.create_all(engine)

# First, put all places into a pandas DataFrame.
places_dataframe = \
    pd.read_csv('ACSDT5Y2018.B01003_data_with_overlays_2020-03-09T011028.csv',\
        skiprows=[1])

places = []

# Iterate through the DataFrame and convert each row to a Place model.
for index, data in places_dataframe.iterrows():
    # Assign our data to temporary variables.
    _id = data['GEO_ID']
    _name = data['NAME']
    _key = key_hash(_name)
    _pop = data['B01003_001E']
    # Create the models.
    places.append(Place(id=_id, key=_key, name=_name, pop=_pop))

# Add the places to our SQLite database.
for place in places:
    session.add(place)
    session.commit()

# Print the five largest places in California for debugging purposes.
for instance in session.query(Place).order_by(Place.pop.desc()).limit(5):
    print(instance)
