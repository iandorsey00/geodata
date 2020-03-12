import pandas as pd

from PlaceCounty import PlaceCounty
from ColumnHeader import ColumnHeader, columns
from initialize_sqlalchemy import Base, engine, session

from model import insert_rows
from key_hash import key_hash

class Database:
    '''Docstring goes here.'''
    ###########################################################################
    # Helper methods for __init__

    # Get the county given a Census name string from summary level 155.
    def get_county(self, geo_name):
        # Split the name string by ", "
        split_geo_name = geo_name.split(", ")
        # Get the first part, which will be of format XXX County (part)
        county_part = split_geo_name[0]
        # Return only the part before " (part)"
        return county_part[:-7]

    # Get the Census place string given a Census name string.
    def get_place(self, geo_name):
        # Split the name string by ", "
        split_geo_name = geo_name.split(", ")
        return ", ".join(split_geo_name[1:])

    # Get the state name given a Sensus name string.
    def get_state(self, geo_name):
        # Split the name string by ", "
        split_geo_name = geo_name.split(", ")
        return split_geo_name[-1]
    
    ###########################################################################
    # __init__

    def __init__(self):
        # Transfer of ColumnHeader data to database ###########################
        insert_rows(ColumnHeader,
                   '../data/ACS_5yr_Seq_Table_Number_Lookup.txt',
                   cols=columns)

        # Prepare PlaceCounties ###############################################

        # Create all tables
        Base.metadata.create_all(engine)

        # First, put all places into a pandas DataFrame.
        places_df = pd.read_csv('../data/g20185ca.csv', encoding='iso-8859-1',
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
            _state = self.get_state(data[49])
            _name = self.get_place(data[49])
            _key = key_hash(_name)
            _county = self.get_county(data[49])
            # For now, look up the population using pandas.
            # Create the models.
            places.append(PlaceCounty(logrecno=_logrecno, geo_id=_geo_id,
            key=_key, state=_state, county=_county, name=_name))

        # Add the places to our SQLite database.
        session.add_all(places)

        # Commit changes
        session.commit()

        # Debug output for ColumnHeaders and PlaceCounties ####################

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

        # Prepare needed data #################################################

        # Specify table_ids and line numbers that have the data we needed.
        # See data/ACS_5yr_Seq_Table_Number_Lookup.txt
        line_numbers_dict = {
            'B01003': ['1'],   # TOTAL POPULATION
            'B19301': ['1'],   # PER CAPITA INCOME IN THE PAST 12 MONTHS (IN
                               # 2018 INFLATION-ADJUSTED DOLLARS)
            'B02001': ['2',    # RACE - White alone
                       '3',    # RACE - Black or African American alone
                       '5'],   # RACE - Asian alone
            'B03002': ['12'],  # HISPANIC OR LATINO ORIGIN BY RACE - Hispanic
                               # or Latino
            # EDUCATIONAL ATTAINMENT FOR THE POPULATION 25 YEARS AND OVER
            'B15003': ['1',    # Total:
                       '22',   # Bachelor's degree
                       '23',   # Master's degree
                       '24',   # Professional school degree
                       '25']   # Doctorate degree
        }

        # Select relevant column headers.
        column_headers = session.query(ColumnHeader) \
            .filter(ColumnHeader.table_id.in_(
                line_numbers_dict.keys()
                )).all()

        # Obtain needed sequence numbers                                  #####
        sequence_numbers = dict()
        this_table_id = ''
        this_sequence_number = ''

        for column_header in column_headers:
            # Have our current table_id available.
            if this_table_id != column_header.table_id:
                this_table_id = column_header.table_id
                # Set the entry for this table to an empty list if it's not
                # available.
                sequence_numbers[this_table_id] = []

            if column_header.sequence_number != this_sequence_number:
                this_sequence_number = column_header.sequence_number
                # Add a new sequence number when we iterate on one.
                sequence_numbers[this_table_id] = this_sequence_number

        print("Needed sequence numbers:", sequence_numbers)

        # Obtain needed files                                             #####

        files = dict()

        for table_id, sequence_number in sequence_numbers.items():
            files[table_id] = "../data/e20185ca" + sequence_number + "000.txt"

        print("Needed files:", files)

        # Obtain needed positions                                         #####

        positions = dict()
        this_start_position = 0
        this_pos = 0

        for column_header in column_headers:
            # Insert the table_id key
            if this_table_id != column_header.table_id:
                this_table_id = column_header.table_id
                positions[this_table_id] = [5]
            # We will hit a start position first.
            if column_header.start_position:
                # Subtract 1, because census start positions start from 1, not
                # 0.
                this_start_position = int(column_header.start_position) - 1
                # After hitting a start position, we'll hit a line number.
            elif column_header.line_number in line_numbers_dict[this_table_id]:
                # Line numbers are offsets from starting positions. But again,
                # they start at 1.
                positions[this_table_id].append(this_start_position + \
                    int(column_header.line_number) - 1)

        print("Needed positions:", positions)

        # Obtain needed column names                                      #####

        column_names = dict()

        for id, line_numbers in line_numbers_dict.items():
            # If it's not in the table yet, initialize a new list with 'LOGRECNO'
            column_names[id] = ['LOGRECNO']
            # Add the table_id, plus and underscore, plus a line number
            for line_number in line_numbers:
                column_names[id].append(id + '_' + line_number)

        print("Needed column names:", column_names)
        print()

        # Organize data #######################################################

        # Get ready to store data in a dictionary of dataframes.
        data_dfs = {}

        for id, line_number in line_numbers_dict.items():
            # Add column 5 because we need the logrecnos.
            data_dfs[id] = pd.read_csv(files[id], usecols=positions[id],
                names=column_names[id], dtype='str', header=None)

        # Merge the values of data_dfs together for easier insertion into our
        # Data SQL table.
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

        # Create our new model ################################################

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
        attr_dict['placecounty'] = relationship('PlaceCounty',
            back_populates='data')

        # attr_dict
        Data = type('Data', (Base,), attr_dict)

        # Create the table in the database
        Base.metadata.create_all(engine)

        # Add relationship to PlaceCounty
        PlaceCounty.data = relationship('Data', uselist=False,
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

        # GeoHeaders ##########################################################

        # The primary reason we are interested in the 2019 National Gazetteer
        # is that we need to get the land area so that we can calculate
        # population and housing unit densities.

        from GeoHeader import GeoHeader

        # Create the table in the database
        Base.metadata.create_all(engine)

        PlaceCounty.geoheader = relationship('GeoHeader', uselist=False, \
            back_populates='placecounty')

        insert_rows(GeoHeader, '../data/2019_Gaz_place_national.txt', sep='\t',
                    dtype='str')

        session.commit()

        print("Geoheaders:", "\n")

        # Print some GeoHeaders for debugging purposes.
        for instance in session.query(GeoHeader).limit(5):
            print(instance)

        print()

        print("PlaceCounty instances with joined Data:", "\n")

        # Joined data #########################################################

        # Get rows of data
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

        print("DataFrame:", "\n")

        # Prepare a DataFrame into which we can insert columns.
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
            # Load data into a list first.
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
            
            # In order to insert rows into the DataFrame, first convert the
            # list into a Pandas series.
            a_series = pd.Series(to_append, index = query_df.columns)
            # Next, append the series to the DataFrame.
            query_df = query_df.append(a_series, ignore_index=True)

        # Convert all data into numeric data, even if there are errors.
        query_df = query_df.apply(pd.to_numeric, errors='coerce')

        print(query_df.head())
        print()

        # Print some debug information.
        print("Medians:", "\n")
        medians = query_df.median()
        print(list(medians))
        print()

        print("Standard deviations:", "\n")
        standard_deviations = query_df.std()
        print(list(standard_deviations))
        print()

        # PlaceVectors ########################################################

        # Now, we are ready to work with PlaceVectors

        from PlaceVector import PlaceVector

        self.placevectors = []

        for instance in all_results:
            try:
                # Construct a PlaceVector and append it to self.PlaceVectors.
                self.placevectors.append(
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
            # If a TypeError is thrown because some data is unavailable, just
            # don't make that PlaceVector and print a debugging message.
            except (TypeError, ValueError):
                print("Note: Inadequate data for PlaceVector creation:",
                      instance.name)

        print()
        search_name = input("Enter the name of a place that you want to compare with others: ")
        filter_county = input("Would you like to filter by a county? If not, just press Enter: ")
        print()

        # Obtain the PlaceVector for which we entered a name.
        comparison_pv = \
            list(filter(lambda x: x.name == search_name, self.placevectors))[0]

        print("The most demographically similar places are:")
        print()

        # Filter by county if a filter_county was specified.
        if filter_county != '':
            filtered_pvs = list(filter(lambda x: x.county == filter_county,
                                self.placevectors))

        # Get the closest PlaceVectors.
        # In other words, get the most demographically similar places.
        closest_pvs = sorted(filtered_pvs,
            key=lambda x: comparison_pv.distance(x))[1:10]

        # Print these PlaceVectors
        for closest_pv in closest_pvs:
            print(closest_pv)
