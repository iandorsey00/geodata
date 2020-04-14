from database.Database import Database

import argparse
import sys
import csv
import numpy
import pickle

from tools.geodata_typecast import gdt, gdtf, gdti

from tools.CountyTools import CountyTools
from tools.StateTools import StateTools
from tools.KeyTools import KeyTools
from tools.SummaryLevelTools import SummaryLevelTools

from rapidfuzz import fuzz

def create_data_products(args):
    '''Generate and save data products.'''
    d = Database(args.path)
    pickle.dump(d.get_products(), open('./bin/default.geodata', 'wb'))

def load_data_products():
    '''Load data products.'''
    with open('./bin/default.geodata', 'rb') as f:
        return pickle.load(f)

def initalize_database():
    '''Load data products or create them if they don't exist.'''
    # Try to open the default database, located at ../bin/default.db.
    try:
        d = load_data_products()
        return d
    # If there is no such database...
    except FileNotFoundError:
        # Print a notice of this and ask the user if they want to create one.
        print('geodata: Database does not exist.')
        print('Enter')
        print()
        print('    geodata createdb -h')
        print()
        print('for more information.')

def context_filter(input_instances, args_context, args_pop_filter, gv=False):
    '''Filters instances and leaves those that match the context.'''
    ct = CountyTools()
    kt = KeyTools()
    slt = SummaryLevelTools()

    universe_sl, group_sl, group = slt.unpack_context(args.context)
    instances = input_instances

    # Filter by summary level
    if universe_sl:
        instances \
            = list(filter(lambda x: x.sumlevel == universe_sl, instances))

    # Filter by group summary level
    if group_sl == '050':
        key = 'us:' + group + '/county'
        county_name = kt.key_to_county_name[key]
        county_geoid = ct.county_name_to_geoid[county_name]

        instances = list(filter(lambda x: county_geoid in x.counties,
                                instances))
    elif group_sl == '040':
        instances = list(filter(lambda x: x.state == group, instances))
    elif group_sl == '860':
        instances = list(filter(lambda x: x.name.startswith('ZCTA5 ' + group),
                                instances))

    # Population
    if args.pop_filter:
        pop_filter = gdt(args_pop_filter)
        instances = list(filter(lambda x: gdti(x.d['population']) > pop_filter,
                                instances))

    return instances

def get_n(args_n, default=15):
    '''Get the number of rows to display.'''
    if args_n < 1:
        raise ValueError("n cannot be less than 1.")
    else:
        return args_n

def compare_geovectors(args, mode='std'):
    '''Compare GeoVectors.'''
    n = get_n(args.n)
    
    d = initalize_database()
    gv_list = d['geovectors']

    # Obtain the GeoVector for which we entered a name.
    comparison_gv = \
        list(filter(lambda x: x.name == args.display_label, gv_list))[0]

    # If a context was specified, filter GeoVector instances
    if args.context:
        gv_list = context_filter(gv_list, args.context, args.pop_filter)
    else:
        gv_list = list(filter(lambda x: x.sumlevel == comparison_gv.sumlevel,
                              gv_list))

    # Get the closest GeoVectors.
    # In other words, get the most demographically similar places.
    closest_pvs = sorted(gv_list,
                    key=lambda x: comparison_gv.distance(x, mode=mode))[:n]

    if len(closest_pvs) == 0:
        print("Sorry, no GeoVectors match your criteria.")
    else:
        if mode == 'std':
            width = 105
        elif mode == 'app':
            width = 85

        print("The most demographically similar geographies are:")
        print()
        print('-' * width)
        if mode == 'std':
            print(' Geography'.ljust(41), 'County'.ljust(20), 'PDN', 'PCI', 'WHT', 'BLK', 'ASN', 'HPL', 'BDH', 'GDH', ' Distance')
        elif mode == 'app':
            print(' Geography'.ljust(41), 'County'.ljust(20), 'PDN', 'PCI', 'MYS', ' Distance')
        print('-' * width)

        # Print these GeoVectors
        for closest_pv in closest_pvs:
            print('', closest_pv.display_row(mode),
                round(comparison_gv.distance(closest_pv, mode=mode), 2))

        print('-' * width)

def compare_geovectors_app(args):
    compare_geovectors(args, mode='app')

def get_dp(args):
    '''Get DemographicProfiles.'''
    d = initalize_database()

    place = args.display_label
    dp = list(filter(lambda x: x.name == place, d['demographicprofiles']))[0]
    print(str(dp))

def superlatives(args, anti=False):
    '''Get superlatives and antisuperlatives.'''
    n = get_n(args.n)
    d = initalize_database()

    st = StateTools()
    kt = KeyTools()
    slt = SummaryLevelTools()

    comp = args.comp
    data_type = args.data_type

    dpi_instances = d['demographicprofiles']
    fetch_one = dpi_instances[0]

    # Determine whether we want components (values that come straight from
    # Census data files) or compounds (values that can only be obtained by
    # math operations involving multiple components).

    # By default, display compounds if there is one for the comp.
    # Otherwise, display a component.
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
    
    # Remove numpy.nans because they interfere with sorted()
    dpi_instances = list(filter(lambda x: not \
                   numpy.isnan(getattr(x, sort_by)[comp]), dpi_instances))

    # Filter instances
    dpi_instances = context_filter(dpi_instances, args.context, args.pop_filter)

    # For the median_year_structure_built component, remove values of zero and
    # 18...
    if args.comp == 'median_year_structure_built':
        dpi_instances = list(filter(lambda x: not \
            x.rc['median_year_structure_built'] == 0, dpi_instances))
        dpi_instances = list(filter(lambda x: not \
            x.rc['median_year_structure_built'] == 18, dpi_instances))

    # Sort our DemographicProfile instances by component or compound specified.
    sls = sorted(dpi_instances, key=lambda x: \
                 getattr(x, sort_by)[comp], reverse=(not anti))

    # helper methods for printing (a)sl rows ##################################

    # The inter-area margin to divide display sections
    iam = ' '

    def divider(dpi):
        '''Print a divider for DemographicProfiles'''
        if args.comp == 'population':
            return '-' * 68
        else:
            return '-' * 89

    def sl_print_headers(comp, universe_sl, group_sl, group):
        '''Helper method to DRY up sl_print_headers'''

        # Set the name of the universe
        if universe_sl:
            if universe_sl == '040':
                universe = 'State'
            elif universe_sl == '050':
                universe = 'County'
            elif universe_sl == '160':
                universe = 'Place'
            elif universe_sl == '310':
                universe = 'Metro/micro area'
            elif universe_sl == '400':
                universe = 'Urban area'
            elif universe_sl == '860':
                universe = 'ZCTA'
        else:
            universe = 'Geography'

        if group:
            group_name = ''

            if group_sl == '040':
                group_name = st.get_name(group)
            elif group_sl == '050':
                key = 'us:' + group + '/county'
                group_name = kt.key_to_county_name[key]
            elif group_sl == '860':
                group_name = group
            
            # Output '<UNIVERSE GEOGRAPHY> in <GROUP NAME>'
            out_str = iam + (universe + ' in ' \
                + group_name).ljust(45)[:45] + iam \
                + getattr(dpi, 'rh')['population'].rjust(20)
        else:
            out_str = iam + universe.ljust(45)[:45] + iam \
                + getattr(dpi, 'rh')['population'].rjust(20)

        # Print another column if the comp isn't population
        if args.comp != 'population':
            out_str += iam + getattr(dpi, 'rh')[comp].rjust(20)[:20]

        return out_str

    # dpi = demographicprofile_instance
    def sl_print_row(dpi):
        '''Print a data row for DemographicProfiles'''
        out_str = iam + getattr(dpi, 'name').ljust(45)[:45] + iam \
                  + getattr(dpi, 'fc')['population'].rjust(20)
        if args.comp != 'population':
            out_str += iam + getattr(dpi, print_)[comp].rjust(20)[:20]
        return out_str

    # Printing ################################################################

    universe_sl, group_sl, group = slt.unpack_context(args.context)

    if len(sls) == 0:
        print("Sorry, no geographies match your criteria.")
    else:
        # Print the header and places with their information.
        dpi = d['demographicprofiles'][0]
        print(divider(dpi))
        print(sl_print_headers(comp, universe_sl, group_sl, group))
        print(divider(dpi))
        for sl in sls[:n]:
            print(sl_print_row(sl))
        print(divider(dpi))

def antisuperlatives(args):
    '''Wrapper function for antisuperlatives.'''
    superlatives(args, anti=True)

def print_search_divider():
    return '-' * 68

def print_search_result(dpi):
    '''Print a row for search results.'''
    iam = ' '

    out_str = iam + getattr(dpi, 'name').ljust(45)[:45] + iam \
                + getattr(dpi, 'fc')['population'].rjust(20)
    return out_str

def display_label_search(args):
    '''Search display labels (place names).'''
    n = get_n(args.n)
    d = initalize_database()

    dpi_instances = d['demographicprofiles']
    dpi_instances = sorted(dpi_instances, key=lambda x: \
                        fuzz.token_set_ratio(args.query, x.name), reverse=True)

    print(print_search_divider())

    iam = ' '
    
    print(iam + 'Search results'.ljust(45)[:45] + iam + \
          'Total population'.rjust(20))

    print(print_search_divider())

    for dpi_instance in dpi_instances[:n]:
        print(print_search_result(dpi_instance))

    print(print_search_divider())

def tocsv(args):
    '''Output data to a CSV file'''
    # Note: n is not yet implemented.
    # TODO: Permit -n 0 to mean 'all values'

    d = initalize_database()
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

    comps = args.comps.split(' ')
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
    dpi_instances = context_filter(dpi_instances, args.context, args.pop_filter)

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

###############################################################################
# Argument parsing with argparse

# Create the top-level argument parser
parser = argparse.ArgumentParser(
    description='Displays information for geographies in the U.S.')
# Create top-level subparsers
subparsers = parser.add_subparsers(
    help='enter geodata <subcommand> -h for more information.')

# Top-level subparser
# Create the parsor for the "createdb" command
createdb_parser = subparsers.add_parser('createdb', aliases=['c'])
createdb_parser.add_argument('path', help='path to data files')
createdb_parser.set_defaults(func=create_data_products)

# Create the parser for the "view" command
view_parsers = subparsers.add_parser('view', aliases=['v'])
# Create subparsers for the "view" command
view_subparsers = view_parsers.add_subparsers(
    help='enter geodata view <subcommand> -h for more information.')

# Create the parser for the "search" command
search_parser = subparsers.add_parser('search', aliases=['s'],
    description='Search for a display label (place name)')
search_parser.add_argument('query', help='search query')
search_parser.add_argument('-n', type=int, default=15, help='number of results to display')
search_parser.set_defaults(func=display_label_search)

# Create the parser for the "tocsv" command
tocsv_parser = subparsers.add_parser('tocsv', aliases=['t'],
    description='Output data in CSV format')
tocsv_parser.add_argument('comps', help='components or compounds to output')
tocsv_parser.add_argument('-p', '--pop_filter', help='filter by population')
tocsv_parser.add_argument('-c', '--context', help='group of geographies')
tocsv_parser.add_argument('-n', type=int, default=0, help='number of rows to display')
tocsv_parser.set_defaults(func=tocsv)

# View subparser
# Create parsors for the view command command
# DemographicProfiles #########################################################
dp_parsor = view_subparsers.add_parser('dp',
    description='View a DemographicProfile.')
dp_parsor.add_argument('display_label', help='the exact place name')
dp_parsor.set_defaults(func=get_dp)

# GeoVectors [standard mode] ##################################################
gv_parsor = view_subparsers.add_parser('gv',
    description='View GeoVectors nearest to a GeoVector.')
gv_parsor.add_argument('display_label', help='the exact place name')
gv_parsor.add_argument('-p', '--pop_filter', help='filter by population')
gv_parsor.add_argument('-c', '--context', help='geographies to compare with')
gv_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
gv_parsor.set_defaults(func=compare_geovectors)

# GeoVectors [appearance mode] ################################################
gva_parsor = view_subparsers.add_parser('gva',
    description='View GeoVectors nearest to a GeoVector [appearance mode]')
gva_parsor.add_argument('display_label', help='the exact place name')
gva_parsor.add_argument('-p', '--pop_filter', help='filter by population')
gva_parsor.add_argument('-c', '--context', help='geographies to compare with')
gva_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
gva_parsor.set_defaults(func=compare_geovectors_app)

# Superlatives ################################################################
sl_parsor = view_subparsers.add_parser('sl',
    description='View places that rank highest with regard to a certain characteristic.')
sl_parsor.add_argument('comp', help='the comp that you want to rank')
sl_parsor.add_argument('-d', '--data_type', help='c: component; cc: compound')
sl_parsor.add_argument('-p', '--pop_filter', help='filter by population')
sl_parsor.add_argument('-c', '--context', help='group of geographies to display')
sl_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
sl_parsor.set_defaults(func=superlatives)

# Antisuperlatives ############################################################
asl_parsor = view_subparsers.add_parser('asl',
    description='View places that rank lowest with regard to a certain characteristic.')
asl_parsor.add_argument('comp', help='the comp that you want to rank')
asl_parsor.add_argument('-d', '--data_type', help='c: component; cc: compound')
asl_parsor.add_argument('-p', '--pop_filter', help='filter by population')
asl_parsor.add_argument('-c', '--context', help='group of geographies to display')
asl_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
asl_parsor.set_defaults(func=antisuperlatives)

# Parse arguments
args = parser.parse_args()
args.func(args)
