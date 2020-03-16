import pandas as pd

from model.PlaceCounty import PlaceCounty
from model.ColumnHeader import get_ch_columns
from model.GeoHeader import get_geoheader_columns
from datainterface.DemographicProfile import DemographicProfile
from initialize_sqlalchemy import Base, engine, session
from itertools import islice
import sqlite3
import csv

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
    # def get_place(self, geo_name):
    #     # Split the name string by ', '
    #     if ';' in geo_name:
    #         split_geo_name = geo_name.split('; ')
    #     else:
    #         split_geo_name = geo_name.split(', ')
    #     return ', '.join(split_geo_name[1:])

    # Get the state name given a Sensus name string.
    def get_state(self, geo_name):
        # Split the name string by ', '
        if ';' in geo_name:
            split_geo_name = geo_name.split('; ')
        else:
            split_geo_name = geo_name.split(', ')
        return split_geo_name[-1]

    def dbapi_qm_substr(self, columns_len):
        '''Get the DBAPI question mark substring'''
        return ', '.join(['?'] * columns_len)

    def dbapi_update_qm_substr(self, columns_len):
        '''Get the DBAPI question mark substring for UPDATE stmts'''
        return ', '.join(['? = ?'] * columns_len)

    # ido = id_offset: Set it to one if there is an id that columns should
    # ignore. Otherwise, if there is no seperate id column, set it 0.
    def create_table(self, table_name, columns, column_defs, rows, ido=1):
        '''Create a table for use by geodata.'''
        # DBAPI question mark substring
        columns_len = len(column_defs) - ido
        question_mark_substr = self.dbapi_qm_substr(columns_len)

        # CREATE TABLE statement
        self.c.execute('''CREATE TABLE %s
                          (%s)''' % (table_name, ', '.join(column_defs)))

        # Insert rows into table
        self.c.executemany('INSERT INTO %s(%s) VALUES (%s)' % (
            table_name, ', '.join(columns), question_mark_substr), rows)

    def debug_output_table(self, table_name):
        '''Print debug information for a table.'''
        print('%s table:' % table_name, '\n')
        for row in self.c.execute('SELECT * FROM %s LIMIT 5' % table_name):
            print(row)
        print()

    def debug_output_list(self, list_name):
        '''Print debug information for a list.'''
        print('%s:' % list_name, '\n')
        for row in getattr(self, list_name)[:5]:
            print(row)
        print()

    def take(self, n, iterable):
        '''Return first n items of the iterable as a list'''
        return list(islice(iterable, n))

    def debug_output_dict(self, dict_name):
        '''Print debug information for a dictionary.'''
        print('%s:' % dict_name, '\n')
        for key, value in self.take(5, getattr(self, dict_name).items()):
            print(key + ':', value)
        print()
    
    ###########################################################################
    # __init__

    def __init__(self, path):
        '''Create the database'''
        self.states = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'dc', 'de',
        'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md',
        'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny',
        'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut',
        'vt', 'va', 'wa', 'wv', 'wi', 'wy']

        self.state_abbrevs = {
            'Alaska': 'AK',
            'Alabama': 'AL',
            'Arkansas': 'AR',
            'American Samoa': 'AS',
            'Arizona': 'AZ',
            'California': 'CA',
            'Colorado': 'CO',
            'Connecticut': 'CT',
            'District of Columbia': 'DC',
            'Delaware': 'DE',
            'Florida': 'FL',
            'Georgia': 'GA',
            'Guam': 'GU',
            'Hawaii': 'HI',
            'Iowa': 'IA',
            'Idaho': 'ID',
            'Illinois': 'IL',
            'Indiana': 'IN',
            'Kansas': 'KS',
            'Kentucky': 'KY',
            'Louisiana': 'LA',
            'Massachusetts': 'MA',
            'Maryland': 'MD',
            'Maine': 'ME',
            'Michigan': 'MI',
            'Minnesota': 'MN',
            'Missouri': 'MO',
            'Northern Mariana Islands': 'MP',
            'Mississippi': 'MS',
            'Montana': 'MT',
            'National': 'NA',
            'North Carolina': 'NC',
            'North Dakota': 'ND',
            'Nebraska': 'NE',
            'New Hampshire': 'NH',
            'New Jersey': 'NJ',
            'New Mexico': 'NM',
            'Nevada': 'NV',
            'New York': 'NY',
            'Ohio': 'OH',
            'Oklahoma': 'OK',
            'Oregon': 'OR',
            'Pennsylvania': 'PA',
            'Puerto Rico': 'PR',
            'Rhode Island': 'RI',
            'South Carolina': 'SC',
            'South Dakota': 'SD',
            'Tennessee': 'TN',
            'Texas': 'TX',
            'Utah': 'UT',
            'Virginia': 'VA',
            'Virgin Islands': 'VI',
            'Vermont': 'VT',
            'Washington': 'WA',
            'Wisconsin': 'WI',
            'West Virginia': 'WV',
            'Wyoming': 'WY'
        }

        # Initialize ##########################################################

        self.path = path

        # Connect to SQLite3
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

        # table_metadata ######################################################
        this_table_name = 'table_metadata'

        # Process column definitions
        columns = get_ch_columns(self.path)
        column_defs = list(map(lambda x: x + ' TEXT', columns))
        column_defs.insert(0, 'id INTEGER PRIMARY KEY')

        # Get rows from CSV
        this_path = self.path + 'ACS_5yr_Seq_Table_Number_Lookup.csv'
        rows = []

        with open(this_path, 'rt') as f:
            rows = list(csv.reader(f))

        # Create table
        self.create_table(this_table_name, columns, column_defs, rows)

        # Debug output
        self.debug_output_table(this_table_name)

        # places ##############################################################
        this_table_name = 'places'

        # Process column definitions
        columns = [
            'LOGRECNO',
            'GEOID',
            'STATE',
            'STATE_ABBREV',
            'NAME',
            ]
        self.places_columns = columns
        column_defs = list(map(lambda x: x + ' TEXT', columns))
        column_defs[1] += ' PRIMARY KEY'

        # Get rows from CSV
        rows = []
        # Get rows from CSV files for each state.
        for state in self.states:
            this_path = path + 'g20185' + state + '.csv'
            with open(this_path, 'rt', encoding='iso-8859-1') as f:
                rows += list(csv.reader(f))
        # Filter for summary level code 160 (State-Places)
        rows = list(filter(lambda x: x[2] == '160', rows))
        rows = list(
                    map(lambda x:
                        [x[4],                  # LOGRECNO
                        x[48][7:],              # GEOID
                        self.get_state(x[49]),  # STATE
                        self.state_abbrevs[self.get_state(x[49])],
                                                # STATE_ABBREV
                        x[49]],                 # NAME
                        rows
                    )
                )

        # DBAPI question mark substring
        columns_len = len(column_defs)
        question_mark_substr = ', '.join(['?'] * columns_len)

        # Create table
        self.create_table(this_table_name, columns, column_defs, rows, ido=0)

        # Debug output
        self.debug_output_table(this_table_name)

        # geoheaders ##########################################################
        this_table_name = 'geoheaders'

        # The primary reason we are interested in the 2019 National Gazetteer
        # is that we need to get the land area so that we can calculate
        # population and housing unit densities.

        columns = get_geoheader_columns(self.path)
        columns[-1] = columns[-1].strip()
        self.geoheaders_columns = columns
        column_defs = list(map(lambda x: x + ' TEXT', columns))
        column_defs[1] += ' PRIMARY KEY'

        # Get rows from CSV
        this_path = self.path + '2019_Gaz_place_national.txt'
        rows = []

        with open(this_path, 'rt') as f:
            rows = list(csv.reader(f, delimiter='\t'))

        for row in rows:
            row[-1] = row[-1].strip()

        # Create table
        self.create_table(this_table_name, columns, column_defs, rows, ido=0)

        # Debug output
        self.debug_output_table(this_table_name)

        # Specify what data we need ###########################################

        # Specify table_ids and line numbers that have the data we need.
        # See data/ACS_5yr_Seq_Table_Number_Lookup.txt
        self.line_numbers_dict = {
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

        # Get needed table metadata.
        self.table_metadata = []

        for table_id, line_numbers in self.line_numbers_dict.items():
            self.table_metadata += self.c.execute('''SELECT * FROM table_metadata
                WHERE table_id = ? AND (line_number IN (%s) OR line_number = '')''' % (
                self.dbapi_qm_substr(len(line_numbers)) ),
                [table_id] + line_numbers)

        self.debug_output_list('table_metadata')

        # Obtain needed sequence numbers                                  #####
        self.sequence_numbers = dict()

        for table_metadata_row in self.table_metadata:
            table_id = table_metadata_row[2]
            sequence_number = table_metadata_row[3]

            # Create the key for the table_id if it doesn't exist.
            if table_id not in self.sequence_numbers.keys():
                self.sequence_numbers[table_id] = []

            self.sequence_numbers[table_id].append(sequence_number)

        # Remove duplicate sequence numbers
        for key, value in self.sequence_numbers.items():
            self.sequence_numbers[key] = list(dict.fromkeys(value))

        self.debug_output_dict('sequence_numbers')

        # Obtain needed files                                             #####
        self.files = dict()

        for table_id, sequence_numbers in self.sequence_numbers.items():
            if table_id not in self.files.keys():
                self.files[table_id] = []

            for state in self.states:
                this_path = self.path + 'e20185' + state + sequence_number \
                            + '000.txt'
                self.files[table_id].append(this_path)
        
        self.debug_output_dict('files')

        # Obtain needed positions                                         #####
        self.positions = dict()
        last_start_position = ''
        last_line_number = ''

        for table_metadata_row in self.table_metadata:
            table_id = table_metadata_row[2]
            start_position = table_metadata_row[5]
            line_number = table_metadata_row[4]

            # If the table_id hasn't been added to the keys yet, set the key
            # to a list containing 5 (the position for LOGRECNO).
            if table_id not in self.positions.keys():
                self.positions[table_id] = [2, 4, 5]

            # Once we hit our start_position, get it and subtract one since
            # they start at one, not zero.
            if start_position:
                last_start_position = int(start_position) - 1

            # If we hit a line number and it's a line number we need, get it,
            # add it to the start_position, then subtract one again since
            # line numbers also start at zero.
            elif line_number in self.line_numbers_dict[table_id]:
                last_line_number = int(line_number)
                self.positions[table_id].append(last_start_position\
                     + last_line_number - 1)
        
        self.debug_output_dict('positions')

        # Obtain needed data_identifiers                                  #####
        self.data_identifiers = dict()
        self.data_identifiers_list = ['STATE', 'SEQUENCE_NUMBER', 'LOGRECNO']

        for table_id, line_numbers in self.line_numbers_dict.items():
            # If there is no such key, start with 'LOGRECNO'
            if table_id not in self.data_identifiers.keys():
                self.data_identifiers[table_id] = \
                    ['STATE', 'SEQUENCE_NUMBER', 'LOGRECNO']

            # Add the data_identifiers.
            # Format: <table_id>_<line_number>
            for line_number in line_numbers:
                this_data_identifier = table_id + '_' + line_number
                self.data_identifiers[table_id].append(this_data_identifier)
                self.data_identifiers_list.append(this_data_identifier)

        self.debug_output_dict('data_identifiers')
        self.debug_output_list('data_identifiers_list')

        # data ################################################################
        this_table_name = 'data'

        print('Processing data table. This might take a while.')
        print()

        columns = self.data_identifiers_list
        self.data_columns = columns
        column_defs = list(map(lambda x: x + ' TEXT', columns))
        column_defs.append('PRIMARY KEY(STATE, SEQUENCE_NUMBER, LOGRECNO)')

        # CREATE TABLE statement
        self.c.execute('''CREATE TABLE %s
                          (%s)''' % (this_table_name, ', '.join(column_defs)))

        # Record whether or not we're on the first statement of the function
        # below.
        first_line_number = True

        # Iterate through table_ids
        for table_id, line_numbers in self.line_numbers_dict.items():
            # Iterate through line_numbers
            for idx, line_number in enumerate(line_numbers):
                # Get ID columns (STATE, SEQUENCE_NUMBER, LOGRECNO) plus the
                # column for the current line_number
                columns = self.data_identifiers[table_id][:3] \
                          + [self.data_identifiers[table_id][3+idx]]
                # Set the question mark substring.
                question_mark_substr = self.dbapi_qm_substr(len(columns))

                # <table_id>_<line_number> = one data identifier.
                # e.g. B01003_1 (Total population)

                # Now, iterate through each file (there is only one file per
                # table per state; we will now iterate through the files
                # for each state.)
                for file in self.files[table_id]:
                    rows = []

                    # Read from each CSV file
                    with open(file, 'rt') as f:
                        csv_rows = csv.reader(f)

                        # Iterate through the rows of the file.
                        for csv_row in csv_rows:
                            this_row = []
                            # Iterate through positions. We will grab
                            # the ID positions plus THE ONE data position
                            # for the current line number.
                            for position in self.positions[table_id][:3] \
                                            + [self.positions[table_id][3+idx]]:
                                position = int(position)
                                if position == 2:
                                    # Upper case the state for conistancy.
                                    this_row.append(csv_row[position].upper())
                                else:
                                    # Append data for that position.
                                    this_row.append(csv_row[position])

                            # For the first iteration, leave the order as it
                            # is. We will be doing INSERT statements.
                            if first_line_number:
                                rows.append(this_row)
                            # Otherwise, adjust the order for an UPDATE
                            # statement.
                            else:
                                rows.append(this_row[3:] + this_row[:3])

                    if first_line_number:
                        # Insert rows into table
                        self.c.executemany('INSERT INTO %s(%s) VALUES (%s)' % (
                            this_table_name, ', '.join(columns),
                            question_mark_substr), rows)
                    else:
                        # UPDATE rows for each data_identifier by (STATE,
                        # SEQUENCE_NUMBER, LOGRECNO) combination.
                        for idx, data_identifier in \
                        enumerate(self.data_identifiers[table_id][3:]):
                            self.c.executemany('''UPDATE %s SET %s = ?
                WHERE STATE = ? AND SEQUENCE_NUMBER = ? AND LOGRECNO = ?''' % (
                                this_table_name, data_identifier), rows)

                # END iteration for the first line number. No more row
                # inserting.
                first_line_number = False

                # Print the count for debug purposes. Should be around ~200,000
                for debug in self.c.execute('SELECT COUNT(*) FROM data'):
                    display_data_identifier = table_id + '_' + line_number
                    print('Processing for', display_data_identifier,
                        'complete.', debug[0], 'rows.')

        print()
        # Debug output
        self.debug_output_table(this_table_name)

        # geodata #############################################################
        this_table_name = 'geodata'

        # Combine data from places, geoheaders, and data into a single table.
        
        # Combine columns
        columns = self.places_columns + self.geoheaders_columns \
                  + self.data_columns
        
        # # Unambiguous columns
        # ub_places_columns = list(map(lambda x: 'places.' + x, self.places_columns))
        # ub_geoheaders_columns = list(map(lambda x: 'geoheaders.' + x, self.geoheaders_columns))
        # ub_data_columns = list(map(lambda x: 'data.' + x, self.data_columns))
        # ub_columns = ub_places_columns + ub_geoheaders_columns + ub_data_columns

        # Make columns names unambigious
        def deambigify(column):
            if column in self.places_columns:
                return 'places.' + column
            elif column in self.geoheaders_columns:
                return 'geoheaders.' + column
            elif column in self.data_columns:
                return 'data.' + column

        # Remove duplicates
        columns = list(dict.fromkeys(columns))
        ub_columns = list(map(deambigify, columns))

        # Column definitions
        column_defs = list(map(lambda x: x + ' TEXT', columns))
        column_defs[1] += ' PRIMARY KEY'

        # DBAPI question mark substring
        columns_len = len(column_defs)
        question_mark_substr = self.dbapi_qm_substr(columns_len)

        # CREATE TABLE statement
        self.c.execute('''CREATE TABLE %s
                          (%s)''' % (this_table_name, ', '.join(column_defs)))

        # Insert rows into merged table
        self.c.execute('''INSERT INTO %s
        SELECT %s FROM places
        JOIN geoheaders ON places.GEOID = geoheaders.GEOID
        JOIN data ON places.LOGRECNO = data.LOGRECNO AND places.STATE_ABBREV = data.STATE''' % (
            this_table_name, ', '.join(ub_columns)))

        # Debug output
        self.debug_output_table(this_table_name)

        # DemographicProfiles #################################################

        # # Get rows of data
        # first_five = session.query(PlaceCounty).limit(5)
        # all_results = session.query(PlaceCounty)

        # # Create a placeholder for DemographicProfiles
        # self.demographicprofiles = []

        # for instance in all_results:
        #     try:
        #         self.demographicprofiles.append(DemographicProfile(instance))
        #     except AttributeError:
        #         print('AttributeError:', instance)

        # print('First five DemographicProfiles:', '\n')

        # for demographicprofile in self.demographicprofiles[:5]:
        #     print(str(demographicprofile))

        # # Prepare a DataFrame into which we can insert rows.
        # rows = []

        # for instance in session.query(PlaceCounty):
        #     try: 
        #         # # Load data into a list first.
        #         # to_append = [
        #         #             instance.data.B01003_1,
        #         #             instance.data.B19301_1,
        #         #             instance.data.B02001_2,
        #         #             instance.data.B02001_3,
        #         #             instance.data.B02001_5,
        #         #             instance.data.B03002_12,
        #         #             instance.data.B15003_1,
        #         #             instance.data.B15003_22,
        #         #             instance.data.B15003_23,
        #         #             instance.data.B15003_24,
        #         #             instance.data.B15003_25,
        #         #             instance.data.B25035_1,
        #         #             instance.data.B25058_1,
        #         #             instance.data.B25077_1,
        #         #             instance.geoheader.ALAND_SQMI,
        #         #             ]
            
        #         # # In order to insert rows into the DataFrame, first convert the
        #         # # list into a Pandas series.
        #         # a_series = pd.Series(to_append, index = query_df.columns)
        #         # # Next, append the series to the DataFrame.
        #         # query_df = query_df.append(a_series, ignore_index=True)
        #         rows.append([[
        #                     instance.data.B01003_1,
        #                     instance.data.B19301_1,
        #                     instance.data.B02001_2,
        #                     instance.data.B02001_3,
        #                     instance.data.B02001_5,
        #                     instance.data.B03002_12,
        #                     instance.data.B15003_1,
        #                     instance.data.B15003_22,
        #                     instance.data.B15003_23,
        #                     instance.data.B15003_24,
        #                     instance.data.B15003_25,
        #                     instance.data.B25035_1,
        #                     instance.data.B25058_1,
        #                     instance.data.B25077_1,
        #                     instance.geoheader.ALAND_SQMI,
        #                     ]])
        #     except AttributeError:
        #         print('AttributeError:', instance)

        # # Convert all data into numeric data, even if there are errors.
        # query_df = pd.DataFrame(rows, columns=column_names + ['ALAND_SQMI'])

        # print('DataFrames:', '\n')
        # print(query_df.head())
        # print()

        # # Print some debug information.
        # print('Medians:', '\n')
        # medians = query_df.median()
        # print(dict(medians))
        # print()

        # print('Standard deviations:', '\n')
        # standard_deviations = query_df.std()
        # print(dict(standard_deviations))
        # print()

        # # PlaceVectors ########################################################

        # from datainterface.PlaceVector import PlaceVector

        # self.placevectors = []

        # for instance in all_results:
        #     try:
        #         # Construct a PlaceVector and append it to self.PlaceVectors.
        #         self.placevectors.append(
        #             PlaceVector(
        #                 instance.name,
        #                 instance.county,
        #                 instance.data.B01003_1,       
        #                 instance.data.B19301_1,       
        #                 instance.data.B02001_2,       
        #                 instance.data.B02001_3,       
        #                 instance.data.B02001_5,       
        #                 instance.data.B03002_12,      
        #                 instance.data.B15003_1,       
        #                 instance.data.B15003_22,      
        #                 instance.data.B15003_23,      
        #                 instance.data.B15003_24,      
        #                 instance.data.B15003_25,      
        #                 instance.geoheader.ALAND_SQMI,
        #                 dict(medians),
        #                 dict(standard_deviations)
        #             )
        #         )
        #     # If a TypeError is thrown because some data is unavailable, just
        #     # don't make that PlaceVector and print a debugging message.
        #     except (TypeError, ValueError, AttributeError):
        #         print('Note: Inadequate data for PlaceVector creation:',
        #               instance.name)

        # # PlaceVectorApps #####################################################

        # from datainterface.PlaceVectorApp import PlaceVectorApp

        # self.placevectorapps = []

        # for instance in all_results:
        #     try:
        #         # Construct a PlaceVector and append it to self.PlaceVectors.
        #         self.placevectorapps.append(
        #             PlaceVectorApp(
        #                 instance.name,
        #                 instance.county,
        #                 instance.data.B01003_1,       
        #                 instance.data.B19301_1,    
        #                 instance.geoheader.ALAND_SQMI,
        #                 instance.data.B25035_1,
        #                 dict(medians),
        #                 dict(standard_deviations)
        #             )
        #         )
        #     # If a TypeError is thrown because some data is unavailable, just
        #     # don't make that PlaceVectorApp and print a debugging message.
        #     except (TypeError, ValueError, AttributeError):
        #         print('Note: Inadequate data for PlaceVectorApp creation:',
        #               instance.name)
