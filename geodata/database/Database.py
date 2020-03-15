import pandas as pd

from model.PlaceCounty import PlaceCounty
from model.ColumnHeader import create_ch_class, get_ch_columns
from datainterface.DemographicProfile import DemographicProfile
from initialize_sqlalchemy import Base, engine, session

from model.model import insert_rows
from key_hash import key_hash

class Database:
    '''Creates a database for use by geodata.'''
    ###########################################################################
    # Helper methods for __init__

    # Get the county given a Census name string from summary level 155.
    def get_county(self, geo_name):
        # Split the name string by ', '
        split_geo_name = geo_name.split(', ')
        # Get the first part, which will be of format XXX County (part)
        county_part = split_geo_name[0]
        # Return only the part before ' (part)'
        return county_part[:-7]

    # Get the Census place string given a Census name string.
    def get_place(self, geo_name):
        # Split the name string by ', '
        if ';' in geo_name:
            split_geo_name = geo_name.split('; ')
        else:
            split_geo_name = geo_name.split(', ')
        return ', '.join(split_geo_name[1:])

    # Get the state name given a Sensus name string.
    def get_state(self, geo_name):
        # Split the name string by ', '
        split_geo_name = geo_name.split(', ')
        return split_geo_name[-1]
    
    ###########################################################################
    # __init__

    def __init__(self, path):
        '''Create the database'''
        self.states = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'dc', 'de',
        'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md',
        'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny',
        'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut',
        'vt', 'va', 'wa', 'wv', 'wi', 'wy']

        # Transfer of ColumnHeader data to database ###########################
        self.path = path

        columns = get_ch_columns(self.path)
        ColumnHeader = create_ch_class(self.path)

        insert_rows(ColumnHeader,
                   self.path + 'ACS_5yr_Seq_Table_Number_Lookup.csv',
                   cols=columns)

        # Prepare PlaceCounties ###############################################

        # Create all tables
        Base.metadata.create_all(engine)

        dfs = [pd.read_csv(path + 'g20185' + state + '.csv',
                    encoding='iso-8859-1', dtype='str', header=None)
                for state in self.states]
        # First, put all places into a pandas DataFrame.
        places_df = pd.concat(dfs, axis=0)
                                
        # Filter for rows where the summary level is 155.
        places_df = places_df.loc[places_df.iloc[:,2] == '155']

        print(places_df.head())

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

        print('Column headers:', '\n')

        # Print the first five column headers for debugging purposes.
        for instance in session.query(ColumnHeader).limit(5):
            print(instance)

        print()

        print('PlaceCounties:', '\n')

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
                       '25'],  # Doctorate degree
            'B25035': ['1'],   # Median year structure built
            'B25058': ['1'],   # Median contract rent (of renter-occupied
                               # housing units)
            'B25077': ['1'],   # Median value (of owner-occupied housing units)
        }

        # Select relevant column headers.
        column_headers = session.query(ColumnHeader) \
            .filter(ColumnHeader.table_id.in_(
                line_numbers_dict.keys()
                )).all()

        # Obtain needed sequence numbers                                  #####
        sequence_numbers = dict()

        # New algorithm. Assumes all members of a table are always in the same
        # sequence:
        for column_header in column_headers:
            table_id = column_header.table_id
            line_number = column_header.line_number
            # If we needed the line number for that table_id, set the
            # sequence_number for table_id to the sequence number for that
            # column_header.
            if line_number in line_numbers_dict[table_id]:
                sequence_numbers[table_id] = column_header.sequence_number

        print('Needed sequence numbers:', sequence_numbers)

        # Obtain needed files                                             #####

        files = dict()

        for table_id, sequence_number in sequence_numbers.items():
            files[table_id] = []
            for state in self.states:
                files[table_id].append(
                    path + 'e20185' + state + sequence_number + '000.txt')

        print('Needed files:', files)

        # Obtain needed positions                                         #####
        positions = dict()

        # Has the logrecno been added to the columns? We only want to add it
        # once.
        logrecno_added = False

        # New algorithm
        for column_header in column_headers:
            # Get table_id
            table_id = column_header.table_id

            # Add LOGRECNO only for the first table_id
            if table_id not in positions.keys():
                if not logrecno_added:
                    positions[table_id] = [5]
                    logrecno_added = True
                else:
                    positions[table_id] = []

            # Once we hit our start_position, get it and subtract one since
            # they start at one, not zero.
            if column_header.start_position:
                start_position = int(column_header.start_position) - 1

            # If we hit a line number and it's a line number we need, get it,
            # add it to the start_position, then subtract one again since
            # line numbers also start at zero.
            elif column_header.line_number in line_numbers_dict[table_id]:
                line_number = int(column_header.line_number)
                positions[table_id].append(start_position + line_number - 1)

        print('Needed positions:', positions)

        # Obtain needed column names                                      #####

        column_name_dict = dict()
        column_names = []
        logrecno_added = False

        for id, line_numbers in line_numbers_dict.items():
            # If it's not in the table yet, initialize a new list with 'LOGRECNO'
            if not logrecno_added:
                column_name_dict[id] = ['LOGRECNO']
                logrecno_added = True
            else:
                column_name_dict[id] = []
            # Add the table_id, plus and underscore, plus a line number
            for line_number in line_numbers:
                column_name = id + '_' + line_number
                column_name_dict[id].append(column_name)
                column_names.append(column_name)

        print('Needed column names by table_id:', column_name_dict)
        print('Needed column names:', column_names)
        print()

        # Organize data #######################################################

        # Get ready to store data in a dictionary of dataframes.
        data_dfs = {}

        for id, line_number in line_numbers_dict.items():
            dfs = [pd.read_csv(f, usecols=positions[id],
                                names=column_name_dict[id],
                                dtype='str', header=None, engine='python') \
                    for f in files[id]]
            data_dfs[id] = pd.concat(dfs, axis=0)

        # Merge the values of data_dfs together for easier insertion into our
        # Data SQL table.
        # First, declare a placeholder.
        # merged_df = pd.DataFrame()
        merged_df = pd.concat(data_dfs.values(), axis=1)

        # for df in data_dfs.values():
        #     # At first, just assign df to merged_df.
        #     if merged_df.empty:
        #         merged_df = df
        #     # For future iterations, merge the DataFrames together.
        #     else:
        #         merged_df = merged_df.set_index('LOGRECNO') \
        #                     .join(df.set_index('LOGRECNO'))
        #         merged_df = merged_df.reset_index()

        print('Merged Data class data:', '\n')
        print(merged_df.head())
        print()

        # Create our new model ################################################

        from model.Data import create_data_class
        from sqlalchemy.orm import relationship

        Data = create_data_class(merged_df)

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

        print('Data instances:', '\n')

        # Print the Data for debugging purposes.
        for instance in session.query(Data).limit(5):
            print(instance)

        print()

        # GeoHeaders ##########################################################

        # The primary reason we are interested in the 2019 National Gazetteer
        # is that we need to get the land area so that we can calculate
        # population and housing unit densities.

        from model.GeoHeader import create_geoheader_class

        GeoHeader = create_geoheader_class(self.path)

        # Create the table in the database
        Base.metadata.create_all(engine)

        PlaceCounty.geoheader = relationship('GeoHeader', uselist=False, \
            back_populates='placecounty')

        insert_rows(GeoHeader, path + '2019_Gaz_place_national.txt', sep='\t',
                    dtype='str')

        session.commit()

        print('Geoheaders:', '\n')

        # Print some GeoHeaders for debugging purposes.
        for instance in session.query(GeoHeader).limit(5):
            print(instance)

        print()

        # DemographicProfiles #################################################

        # Get rows of data
        first_five = session.query(PlaceCounty).limit(5)
        all_results = session.query(PlaceCounty)

        # Create a placeholder for DemographicProfiles
        self.demographicprofiles = []

        for instance in all_results:
            try:
                self.demographicprofiles.append(DemographicProfile(instance))
            except AttributeError:
                print('AttributeError:', instance)

        print('First five DemographicProfiles:', '\n')

        for demographicprofile in self.demographicprofiles[:5]:
            print(str(demographicprofile))

        print('DataFrames:', '\n')

        # Prepare a DataFrame into which we can insert rows.
        query_df = pd.DataFrame(columns=column_names + ['ALAND_SQMI'])

        for instance in session.query(PlaceCounty):
            try: 
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
                            instance.data.B25035_1,
                            instance.data.B25058_1,
                            instance.data.B25077_1,
                            instance.geoheader.ALAND_SQMI,
                            ]
            
                # In order to insert rows into the DataFrame, first convert the
                # list into a Pandas series.
                a_series = pd.Series(to_append, index = query_df.columns)
                # Next, append the series to the DataFrame.
                query_df = query_df.append(a_series, ignore_index=True)
            except AttributeError:
                print('AttributeError:', instance)

        # Convert all data into numeric data, even if there are errors.
        query_df = query_df.apply(pd.to_numeric, errors='coerce')

        print(query_df.head())
        print()

        # Print some debug information.
        print('Medians:', '\n')
        medians = query_df.median()
        print(dict(medians))
        print()

        print('Standard deviations:', '\n')
        standard_deviations = query_df.std()
        print(dict(standard_deviations))
        print()

        # PlaceVectors ########################################################

        from datainterface.PlaceVector import PlaceVector

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
                        dict(medians),
                        dict(standard_deviations)
                    )
                )
            # If a TypeError is thrown because some data is unavailable, just
            # don't make that PlaceVector and print a debugging message.
            except (TypeError, ValueError, AttributeError):
                print('Note: Inadequate data for PlaceVector creation:',
                      instance.name)

        # PlaceVectorApps #####################################################

        from datainterface.PlaceVectorApp import PlaceVectorApp

        self.placevectorapps = []

        for instance in all_results:
            try:
                # Construct a PlaceVector and append it to self.PlaceVectors.
                self.placevectorapps.append(
                    PlaceVectorApp(
                        instance.name,
                        instance.county,
                        instance.data.B01003_1,       
                        instance.data.B19301_1,    
                        instance.geoheader.ALAND_SQMI,
                        instance.data.B25035_1,
                        dict(medians),
                        dict(standard_deviations)
                    )
                )
            # If a TypeError is thrown because some data is unavailable, just
            # don't make that PlaceVectorApp and print a debugging message.
            except (TypeError, ValueError, AttributeError):
                print('Note: Inadequate data for PlaceVectorApp creation:',
                      instance.name)

    def get_data(self):
        return ProcessedData(placevectors=self.placevectors,
                             placevectorapps=self.placevectorapps,
                             demographicprofiles=self.demographicprofiles)


