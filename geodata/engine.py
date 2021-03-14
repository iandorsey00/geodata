from database.Database import Database

import argparse
import copy
import sys
import csv
import numpy
import pickle
import geopy.distance

from tools.geodata_typecast import gdt, gdtf, gdti

from tools.CountyTools import CountyTools
from tools.StateTools import StateTools
from tools.KeyTools import KeyTools
from tools.SummaryLevelTools import SummaryLevelTools

from math import sin, cos, sqrt, atan2, radians

from rapidfuzz import fuzz

class Engine:
    def __init__(self):
        self.initialize_database()

        self.ct = CountyTools()
        self.st = StateTools()
        self.kt = KeyTools()
        self.slt = SummaryLevelTools()
            
    def create_data_products(self, path):
        '''Generate and save data products.'''
        d = Database(path)
        pickle.dump(d.get_products(), open('./bin/default.geodata', 'wb'))

    def load_data_products(self):
        '''Load data products.'''
        with open('./bin/default.geodata', 'rb') as f:
            return pickle.load(f)

    def initialize_database(self):
        '''Load data products or create them if they don't exist.'''
        # Try to open the default database, located at ../bin/default.db.
        self.d = self.load_data_products()

    def get_data_products(self):
        return copy.deepcopy(self.d)

    def get_data_types(self, comp, data_type, fetch_one):
        '''
        Determine whether we want components (values that come straight from
        Census data files) or compounds (values that can only be obtained by
        math operations involving multiple components).

        By default, display compounds if there is one for the comp.
        Otherwise, display a component.
        '''
        if not data_type:
            if comp in fetch_one.c.keys():
                sort_by = 'c'
                print_ = 'fcd'
            else:
                sort_by = 'rc'
                print_ = 'fc'
        # User input 'c', so display a component
        elif data_type == 'c':
            sort_by = 'rc'
            print_ = 'fc'
        # User input 'cc' (or anything else...), so display a compound
        else:
            sort_by = 'c'
            print_ = 'fcd'

        return (sort_by, print_)

    def context_filter(self, input_instances, context, filter, gv=False):
        '''Filters instances and leaves those that match the context.'''
        universe_sl, group_sl, group = self.slt.unpack_context(context)
        instances = input_instances
        fetch_one = instances[0]

        # Filter by summary level
        if universe_sl:
            instances \
                = list(filter(lambda x: x.sumlevel == universe_sl, instances))

        # Filter by group summary level
        if group_sl == '050':
            key = 'us:' + group + '/county'
            county_name = self.kt.key_to_county_name[key]
            county_geoid = self.ct.county_name_to_geoid[county_name]

            instances = list(filter(lambda x: county_geoid in x.counties,
                                    instances))
        elif group_sl == '040':
            instances = list(filter(lambda x: x.state == group, instances))
        elif group_sl == '860':
            instances = list(filter(lambda x: x.name.startswith('ZCTA5 ' + group),
                                    instances))

        # Filtering
        if filter:
            # Convert pipe-delimited criteria string to a list of criteria
            filter_criteria = filter.split('+')
            # Covert list of criteria to lists of lists
            filter_criteria = map(lambda x: x.split(':'), filter_criteria)

            for filter_criterium in filter_criteria:
                # Determine if a data_type was specified
                if len(filter_criterium) == 4:
                    # If so, set the data_type
                    data_type = filter_criterium[3]
                else:
                    # Otherwise, set it to false
                    data_type = False

                comp = filter_criterium[0]
                filter_by, print_ = self.get_data_types(comp, data_type, fetch_one)
                operator = filter_criterium[1]

                # The value is a index 2; convert using geodata_typecast
                value = gdt(filter_criterium[2])

                # Now, filter by operator at index 1.
                if operator == 'gt':
                    instances = list(filter(lambda x: getattr(x, filter_by)[comp] > value, instances))
                elif operator == 'gteq':
                    instances = list(filter(lambda x: getattr(x, filter_by)[comp] >= value, instances))
                elif operator == 'eq':
                    instances = list(filter(lambda x: getattr(x, filter_by)[comp] == value, instances))
                elif operator == 'lteq':
                    instances = list(filter(lambda x: getattr(x, filter_by)[comp] <= value, instances))
                elif operator == 'lt':
                    instances = list(filter(lambda x: getattr(x, filter_by)[comp] < value, instances))
                # It is an error if the value specified is invalid.
                else:
                    raise ValueError("filter: Invalid operator")

        return instances

    def compare_geovectors(self, display_label, context='', n=10, mode='std'):
        '''Compare GeoVectors.'''
        d = self.get_data_products()

        gv_list = d['geovectors']

        # Obtain the GeoVector for which we entered a name.
        comparison_gv = \
            list(filter(lambda x: x.name == display_label, gv_list))[0]

        # If a context was specified, filter GeoVector instances
        if context:
            gv_list = self.context_filter(gv_list, context, False)
        else:
            gv_list = list(filter(lambda x: x.sumlevel == comparison_gv.sumlevel,
                                gv_list))

        # Get the closest GeoVectors.
        # In other words, get the most demographically similar places.
        return sorted(gv_list,
                        key=lambda x: comparison_gv.distance(x, mode=mode))[:n]

    def compare_geovectors_app(self, display_label, context='', n=10):
        return self.compare_geovectors(display_label, context=context, n=n, mode='app')

    def get_dp(self, display_label):
        '''Get DemographicProfiles.'''
        d = self.get_data_products()

        place = display_label
        return list(filter(lambda x: x.name == place, d['demographicprofiles']))[0]

    def extreme_values(self, comp, data_type='c', context='', geofilter='', lowest=False):
        '''Get highest and lowest values.'''
        d = self.get_data_products()

        comp = comp
        data_type = data_type

        dpi_instances = d['demographicprofiles']
        fetch_one = dpi_instances[0]

        sort_by, print_ = self.get_data_types(comp, data_type, fetch_one)
        
        # Remove numpy.nans because they interfere with sorted()
        dpi_instances = list(filter(lambda x: not \
                    numpy.isnan(getattr(x, sort_by)[comp]), dpi_instances))

        # Filter instances
        dpi_instances = self.context_filter(dpi_instances, context, geofilter)

        # For the median_year_structure_built component, remove values of zero and
        # 18...
        if comp == 'median_year_structure_built':
            dpi_instances = list(filter(lambda x: not \
                x.rc['median_year_structure_built'] == 0, dpi_instances))
            dpi_instances = list(filter(lambda x: not \
                x.rc['median_year_structure_built'] == 18, dpi_instances))

        # Sort our DemographicProfile instances by component or compound specified.
        return sorted(dpi_instances, key=lambda x: \
                    getattr(x, sort_by)[comp], reverse=(not lowest))

    def lowest_values(self, comp, data_type='c', context='', geofilter=''):
        '''Wrapper function for lowest values.'''
        return self.extreme_values(comp, data_type=data_type, context=context, geofilter=geofilter, lowest=True)

    def display_label_search(self, query, n=10):
        '''Search display labels (place names).'''
        d = self.get_data_products()

        dpi_instances = d['demographicprofiles']
        return sorted(dpi_instances, key=lambda x: \
                            fuzz.token_set_ratio(query, x.name), reverse=True)

    def rows(self, comps, context='', geofilter=''):
        '''Output data to a CSV file'''
        # Note: n is not yet implemented.
        # TODO: Permit -n 0 to mean 'all values'

        d = self.get_data_products()
        dpi_instances = d['demographicprofiles']
        fetch_one = dpi_instances[0]

        # Categories: Groups of >= 1 comp(s)
        categories = {
            ':geography': ['land_area'],

            ':population': ['population',
                            'population_density'],

            ':race': ['white_alone', 
                    'white_alone_not_hispanic_or_latino',
                    'black_alone',
                    'asian_alone',
                    'other_race',
                    'hispanic_or_latino'],

            ':education': ['population_25_years_and_older',
                            'bachelors_degree_or_higher',
                            'graduate_degree_or_higher'],

            ':income': ['per_capita_income',
                        'median_household_income'],

            ':housing': ['median_year_structure_built',
                        'median_rooms',
                        'median_value',
                        'median_rent'],
        }

        comps = comps.split(' ')
        comp_list = list()

        # Replace categories with comps and validate comps
        for comp in comps:
            if comp in categories.keys():
                comp_list += categories[comp]
            elif comp in fetch_one.rh:
                comp_list += [comp]
            else:
                raise ValueError(comp + ': Invalid comp')

        # Filter instances
        dpi_instances = self.context_filter(dpi_instances, context, geofilter)

        if len(dpi_instances) == 0:
            raise ValueError('Sorry, no geographies match your criteria.')

        # Intialize csvwriter
        csvwriter = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)

        # Header row
        this_row = ['Geography', 'County']

        for comp in comp_list:
            if comp in fetch_one.rc.keys() and comp in fetch_one.c.keys():
                this_row += [fetch_one.rh[comp] + ' (c)']
                this_row += [fetch_one.rh[comp] + ' (cc)']
            else:
                this_row += [fetch_one.rh[comp]]

        csvwriter.writerow(this_row)

        # All other rows
        for dpi_instance in dpi_instances:
            this_row = [dpi_instance.name, ', '.join(dpi_instance.counties_display)]

            for comp in comp_list:
                if comp in dpi_instance.rc.keys() and comp in dpi_instance.c.keys():
                    this_row += [dpi_instance.fc[comp]]
                    this_row += [dpi_instance.fcd[comp]]
                elif comp in dpi_instance.rc:
                    this_row += [dpi_instance.fc[comp]]
                else:
                    this_row += [dpi_instance.fcd[comp]]

            csvwriter.writerow(this_row)

    def get_csv_dp(self, display_label):
        '''Output a DemographicProfile in CSV format'''
        d = self.get_data_products()

        place = display_label
        dp = list(filter(lambda x: x.name == place, d['demographicprofiles']))[0]
        dp.tocsv()

    def get_distance(self, dp1, dp2, kilometers=False):
        '''Distance between two sets of lat/long coords from DemographicProfiles'''

        coords1 = (dp1.rc['latitude'], dp1.rc['longitude'])
        coords2 = (dp2.rc['latitude'], dp2.rc['longitude'])

        if kilometers:
            distance = geopy.distance.distance(coords1, coords2).km
        else:
            distance = geopy.distance.distance(coords1, coords2).mi

        return distance

    def distance(self, display_label_1, display_label_2, kilometers=False):
        '''Get the distance between two geographies'''
        d = self.get_data_products()

        dl1 = display_label_1
        dl2 = display_label_2
        dp1 = list(filter(lambda x: x.name == dl1, d['demographicprofiles']))[0]
        dp2 = list(filter(lambda x: x.name == dl2, d['demographicprofiles']))[0]

        return self.get_distance(dp1, dp2, kilometers)

    def closest_geographies(self, display_label, context='', geofilter=''):
        '''Display the closest geographies'''
        d = self.get_data_products()

        target_geo = list(filter(lambda x: x.name == display_label, d['demographicprofiles']))[0]
        dpi_instances = d['demographicprofiles']
        
        # Remove numpy.nans because they interfere with sorted()
        # dpi_instances = list(filter(lambda x: not \
        #                numpy.isnan(getattr(x, sort_by)[comp]), dpi_instances))

        # Filter instances
        dpi_instances = self.context_filter(dpi_instances, context, geofilter)

        # Get distances
        dp_distances = []

        for dp in dpi_instances:
            if dp.name != target_geo.name:
                dp_distances.append((dp, self.get_distance(target_geo, dp)))

        # Sort our DemographicProfile instances by component or compound specified.
        return sorted(dp_distances, key=lambda x: x[1])