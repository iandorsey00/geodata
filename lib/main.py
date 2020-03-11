#
# main.py
#
# The main project file.
#

import pandas as pd

from PlaceCounty import PlaceCounty
from ColumnHeader import ColumnHeader, columns
from initialize_sqlalchemy import Base, engine, session

from key_hash import key_hash

###############################################################################
# ColumnHeaders

# Create the table
Base.metadata.create_all(engine)

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

# Add column headers to database
session.add_all(column_headers)

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
Base.metadata.create_all(engine)

# First, put all places into a pandas DataFrame.
places_df = pd.read_csv('../data/g20185ca.csv', encoding='iso-8859-1', \
dtype='str', header=None)
# Filter for rows where the summary level is 155.
places_df = places_df.loc[places_df.iloc[:,2] == '155']

# Declare an array to hold instances of PlaceCounty.
places = []

# Iterate through the DataFrame and convert each row to a Place model.
for index, data in places_df.iterrows():
    # Assign our data to temporary variables.

    # LOGRECNO matches a geo entry with its data.
    _logrecno = data[4]
    _geo_id = data[48][7:14]
    _state = 'California'
    _name = get_place(data[49])
    _key = key_hash(_name)
    _county = get_county(data[49])
    # For now, look up the population using pandas.
    # Create the models.
    places.append(PlaceCounty(logrecno=_logrecno, geo_id=_geo_id, key=_key, \
    state=_state, county=_county, name=_name))

# Add the places to our SQLite database.
session.add_all(places)

# Commit changes
session.commit()

print("Column headers:", "\n")

# Print the first five column headers for debugging purposes.
for instance in session.query(ColumnHeader).limit(5):
    print(instance)

print()

print("PlaceCounties:", "\n")

# Print the five largest places in California for debugging purposes.
for instance in session.query(PlaceCounty).limit(5):
    print(instance)

print()

# Specify table_ids and line numbers that have the data we needed.
# See data/ACS_5yr_Seq_Table_Number_Lookup.txt
ids_and_line_numbers_for_needed_tables = {
    'B01003': ['1'],   # TOTAL POPULATION
    'B19301': ['1'],   # PER CAPITA INCOME IN THE PAST 12 MONTHS (IN 2018
                       # INFLATION-ADJUSTED DOLLARS)
    'B02001': ['2',    # RACE - White alone
               '3',    # RACE - Black or African American alone
               '5'],   # RACE - Asian alone
    'B03002': ['12'],  # HISPANIC OR LATINO ORIGIN BY RACE - Hispanic or Latino
    # EDUCATIONAL ATTAINMENT FOR THE POPULATION 25 YEARS AND OVER
    'B15003': ['1',    # Total:
               '22',   # Bachelor's degree
               '23',   # Master's degree
               '24',   # Professional school degree
               '25']   # Doctorate degree
}

print("Other debugging information:", "\n")

# Select relevant column headers.
needed_column_headers = session.query(ColumnHeader) \
    .filter(ColumnHeader.table_id.in_(
        ids_and_line_numbers_for_needed_tables.keys()
        )).all()

# Obtain needed sequence numbers ##############################################
needed_sequence_numbers = dict()
this_table_id = ''
this_sequence_number = ''

for needed_column_header in needed_column_headers:
    # Have our current table_id available.
    if this_table_id != needed_column_header.table_id:
        this_table_id = needed_column_header.table_id
        # Set the entry for this table to an empty list if it's not available.
        needed_sequence_numbers[this_table_id] = []

    if needed_column_header.sequence_number != this_sequence_number:
        this_sequence_number = needed_column_header.sequence_number
        # Add a new sequence number when we iterate on one.
        needed_sequence_numbers[this_table_id] = this_sequence_number

print("Needed sequence numbers:", needed_sequence_numbers)

# Obtain needed files #########################################################

needed_files = dict()

for table_id, sequence_numbers in needed_sequence_numbers.items():
    needed_files[table_id] = "../data/e20185ca" + sequence_numbers + "000.txt"

print("Needed files:", needed_files)

# Obtain needed positions #####################################################

needed_positions = dict()
this_starting_position = 0
this_position = 0

for needed_column_header in needed_column_headers:
    # Insert the table_id key
    if this_table_id != needed_column_header.table_id:
        this_table_id = needed_column_header.table_id
        needed_positions[this_table_id] = [5]
    # We will hit a start position first.
    if needed_column_header.start_position:
        # Subtract 1, because census start positions start from 1, not 0.
        this_starting_position = int(needed_column_header.start_position) - 1
        # After hitting a start position, we'll hit a line number.
    elif needed_column_header.line_number in \
        ids_and_line_numbers_for_needed_tables[this_table_id]:
        # Line numbers are offsets from starting positions. But again, they
        # start at 1.
        needed_positions[this_table_id].append(this_starting_position + \
            int(needed_column_header.line_number) - 1)

print("Needed positions:", needed_positions)

# Obtain needed column names ##################################################

needed_column_names = dict()

for id, line_numbers in ids_and_line_numbers_for_needed_tables.items():
    # If it's not in the table yet, initialize a new list with 'LOGRECNO'
    needed_column_names[id] = ['LOGRECNO']
    # Add the table_id, plus and underscore, plus a line number
    for line_number in line_numbers:
        needed_column_names[id].append(id + '_' + line_number)

print("Needed column names:", needed_column_names)
print()

###############################################################################

# Get ready to store data in a dictionary of dataframes.
data_dfs = {}

for id, line_number in ids_and_line_numbers_for_needed_tables.items():
    # Add column 5 because we need the logrecnos.
    data_dfs[id] = pd.read_csv(needed_files[id], \
        usecols=needed_positions[id], names=needed_column_names[id], \
        dtype='str', header=None)

# Merge the values of data_dfs together for easier insertion into our Data
# SQL table.
# First, declare a placeholder.
merged_df = pd.DataFrame()

for df in data_dfs.values():
    # At first, just assign df to merged_df.
    if merged_df.empty:
        merged_df = df
    # For future iterations, merge the DataFrames together.
    else:
        merged_df = merged_df.set_index('LOGRECNO') \
                    .join(df.set_index('LOGRECNO'))
        merged_df = merged_df.reset_index()

print("Merged Data class data:", "\n")
print(merged_df.head())
print()

###############################################################################
# Create our new model

from sqlalchemy import Column, Integer, String, Index, ForeignKey
from sqlalchemy.orm import relationship

# Dynamic table creation: Create an attr_dict to store table attributes
attr_dict = {}

# Set the name for the table.
attr_dict['__tablename__'] = 'data'

# Give the table an id column
attr_dict['id'] = Column(Integer, primary_key=True)

# Dynamically add the other columns
for column in merged_df.columns:
    if column == 'LOGRECNO':
        attr_dict[column] = Column(String, 
            ForeignKey('place_counties.logrecno'))
    else:
        attr_dict[column] = Column(String)

# Define the __repr__ for the new class
def _repr(self):
    return "<Data(LOGRECNO='%s' ...)>" % (self.LOGRECNO)

# Add the definition above to the class
attr_dict['__repr__'] = _repr

# Add the relationship
attr_dict['placecounty'] = relationship('PlaceCounty', back_populates='data')

# attr_dict
Data = type('Data', (Base,), attr_dict)

# Create the table in the database
Base.metadata.create_all(engine)

# Add relationship to PlaceCounty
PlaceCounty.data = relationship('Data', uselist=False, \
    back_populates='placecounty')

data_rows = []

for index, data in merged_df.iterrows():
    # Create column header models
    record = Data()

    for column in merged_df.columns:
        # Dynamically assign data to each attribute
        setattr(record, column, data[column])
    
    data_rows.append(record)

# Add column headers to database
session.add_all(data_rows)

session.commit()

print("Data instances:", "\n")

# Print the Data for debugging purposes.
for instance in session.query(Data).limit(5):
    print(instance)

print()

###############################################################################
# GeoHeaders
#
# The primary reason we are interested in the 2019 National Gazetteer is to
# to get the land area so that we can calculate population and housing unit
# densities.
#

from GeoHeader import GeoHeader

# Create the table in the database
Base.metadata.create_all(engine)

PlaceCounty.geoheader = relationship('GeoHeader', uselist=False, \
    back_populates='placecounty')

# Declare a place holder for 
geoheader_rows = []

gh_df = pd.read_csv('../data/2019_Gaz_place_national.txt', sep='\t',
dtype='str')

for idx, data in gh_df.iterrows():
    gh_data = GeoHeader()

    for column in gh_df.columns:
        # Dynamically assign data to each attribute
        setattr(gh_data, column, data[column])

    geoheader_rows.append(gh_data)

session.add_all(geoheader_rows)

session.commit()

print("Geoheaders:", "\n")

# Print some GeoHeaders for debugging purposes.
for instance in session.query(GeoHeader).limit(5):
    print(instance)

print()

print("PlaceCounty instances with joined Data:", "\n")

###############################################################################

# Final query: Print 5 records from PlaceCounty with the population and all
# records joined to it.
first_five = session.query(PlaceCounty).limit(5)

all_results = session.query(PlaceCounty)

for instance in first_five:
    print(
    instance, "\n",
    "Population:", instance.data.B01003_1, "\n",                   # 0
    "Per capita income:", instance.data.B19301_1, "\n",            # 1
    "White alone:", instance.data.B02001_2, "\n",                  # 2
    "Black alone:", instance.data.B02001_3, "\n",                  # 3
    "Asian alone:", instance.data.B02001_5, "\n",                  # 4
    "Hispanic or Latino alone:", instance.data.B03002_12, "\n",    # 5
    "Population 25 years and over:", instance.data.B15003_1, "\n", # 6
    "Bachelor's degree:", instance.data.B15003_22, "\n",           # 7               
    "Master's degree:", instance.data.B15003_23, "\n",             # 8   
    "Professional school degree:", instance.data.B15003_24, "\n",  # 9 
    "Doctorate degree:", instance.data.B15003_25, "\n",            # 10
    "Land area:", instance.geoheader.ALAND_SQMI                    # 11
    )

print()
search_name = input("Enter the name of a place for which you would like to look up data: ")
print()

for instance in all_results.filter(PlaceCounty.name == search_name):
    print(
    instance, "\n",
    "Population:", instance.data.B01003_1, "\n",                   # 0
    "Per capita income:", instance.data.B19301_1, "\n",            # 1
    "White alone:", instance.data.B02001_2, "\n",                  # 2
    "Black alone:", instance.data.B02001_3, "\n",                  # 3
    "Asian alone:", instance.data.B02001_5, "\n",                  # 4
    "Hispanic or Latino alone:", instance.data.B03002_12, "\n",    # 5
    "Population 25 years and over:", instance.data.B15003_1, "\n", # 6
    "Bachelor's degree:", instance.data.B15003_22, "\n",           # 7               
    "Master's degree:", instance.data.B15003_23, "\n",             # 8   
    "Professional school degree:", instance.data.B15003_24, "\n",  # 9 
    "Doctorate degree:", instance.data.B15003_25, "\n",            # 10
    "Land area:", instance.geoheader.ALAND_SQMI                    # 11
    )

print()

print("DataFrame:", "\n")

query_df = pd.DataFrame(columns=[
            'B01003_1',
            'B19301_1',
            'B02001_2',
            'B02001_3',
            'B02001_5',
            'B03002_12',
            'B15003_1',
            'B15003_22',
            'B15003_23',
            'B15003_24',
            'B15003_25',
            'ALAND_SQMI'
        ])

for instance in session.query(PlaceCounty):
    to_append = [
                instance.data.B01003_1,
                instance.data.B19301_1,
                instance.data.B02001_2,
                instance.data.B02001_3,
                instance.data.B02001_5,
                instance.data.B03002_12,
                instance.data.B15003_1,
                instance.data.B15003_22,
                instance.data.B15003_23,
                instance.data.B15003_24,
                instance.data.B15003_25,
                instance.geoheader.ALAND_SQMI
                ]
    
    a_series = pd.Series(to_append, index = query_df.columns)
    query_df = query_df.append(a_series, ignore_index=True)

query_df = query_df.apply(pd.to_numeric, errors='coerce')

print(query_df.head())
print()

print("Medians:", "\n")
medians = query_df.median()
print(list(medians))
print()

print("Standard deviations:", "\n")
standard_deviations = query_df.std()
print(list(standard_deviations))
print()

###############################################################################
# PlaceVectors

print("First five PlaceVectors:", "\n")

from PlaceVector import PlaceVector

for instance in first_five:
    print(
        PlaceVector(
            instance.name,
            instance.county,
            instance.data.B01003_1,       
            instance.data.B19301_1,       
            instance.data.B02001_2,       
            instance.data.B02001_3,       
            instance.data.B02001_5,       
            instance.data.B03002_12,      
            instance.data.B15003_1,       
            instance.data.B15003_22,      
            instance.data.B15003_23,      
            instance.data.B15003_24,      
            instance.data.B15003_25,      
            instance.geoheader.ALAND_SQMI,
            list(medians),
            list(standard_deviations)
        )
    )

print()
search_name = input("Enter the name of a place for which you would like to look up a PlaceVector: ")
print()

for instance in all_results.filter(PlaceCounty.name == search_name):
    print(
        PlaceVector(
            instance.name,
            instance.county,
            instance.data.B01003_1,       
            instance.data.B19301_1,       
            instance.data.B02001_2,       
            instance.data.B02001_3,       
            instance.data.B02001_5,       
            instance.data.B03002_12,      
            instance.data.B15003_1,       
            instance.data.B15003_22,      
            instance.data.B15003_23,      
            instance.data.B15003_24,      
            instance.data.B15003_25,      
            instance.geoheader.ALAND_SQMI,
            list(medians),
            list(standard_deviations)
        )
    )
