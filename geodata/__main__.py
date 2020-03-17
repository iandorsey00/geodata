from database.Database import Database
import argparse
import sys
import numpy
import pickle
from tools.geodata_typecast import gdt, gdtf, gdti

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
        print('Default database does not exist.')
        print('Would you like to create one?')
        print("Enter 'y' for yes or anything else for no.")
        response = input()

        # If the user wants to create a database, enter 'y'.
        if response == 'y':
            create_data_products()
            d = load_data_products()
            return d
        # Otherwise, exit.
        else:
            sys.exit(0)

def compare_placevectors(args, type='placevector'):
    '''
    Compare certain types of PlaceVectors.
    type options:
    placevector         PlaceVector (default)
    placevectorapp      PlaceVectorApp
    '''
    d = initalize_database()

    if type == 'placevector':
        pv_list = d['placevectors']
    elif type == 'placevectorapp':
        pv_list = d['placevectorapps']

    # Split the geos with a pipe
    geo_split = args.census_place_string.split('|')

    search_name = geo_split[0]

    # See if the is a filter_state specified. If not, set it to an empty
    # string.
    if len(geo_split) > 1:
        filter_state = geo_split[1]
    else:
        filter_state = ''

    # Obtain the PlaceVector for which we entered a name.
    comparison_pv = \
        list(filter(lambda x: x.name == search_name, pv_list))[0]

    print("The most demographically similar places are:")
    print()

    # Filter by arguments:
    if args.context or args.pop_filter:
        # Context
        if args.context:
            pv_list = list(filter(lambda x: x.state == args.context,
                                pv_list))
        # Population
        if args.pop_filter:
            pop_filter = gdt(args.pop_filter)
            pv_list = list(filter(lambda x: x.population > pop_filter,
                                pv_list))

    # Get the closest PlaceVectors.
    # In other words, get the most demographically similar places.
    closest_pvs = sorted(pv_list,
        key=lambda x: comparison_pv.distance(x))[:6]

    # Print these PlaceVectors
    for closest_pv in closest_pvs:
        print(closest_pv)
        print("Distance:", comparison_pv.distance(closest_pv))

def compare_placevectorapps(args):
    '''Compare PlaceVectorApps.'''
    compare_placevectors(args, type='placevectorapp')

def get_dp(args):
    '''Get DemographicProfiles.'''
    d = initalize_database()

    place = args.census_place_string
    dp = list(filter(lambda x: x.name == place, d['demographicprofiles']))[0]
    print(str(dp))

def superlatives(args, anti=False):
    '''Get superlatives and antisuperlatives.'''
    d = initalize_database()

    comp_name = args.comp_name
    data_type = args.data_type

    # If a pop_filter was specified, parse it.
    if args.pop_filter:
        args.pop_filter = gdti(args.pop_filter)

    # Determine whether we want components (values that come straight from
    # Census data files) or compounds (values that can only be obtained by
    # math operations involving multiple components).
    if data_type == 'c':
        sort_by = 'rc'
        print_ = 'fc'
    else:
        sort_by = 'c'
        print_ = 'fcd'

    # The inter-area margin to divide display sections
    iam = ' '

    # Print a section divider
    def divider():
        return '-' * 89

    # Print the header
    def sl_print_headers(dpi):
        if args.context:
            return iam + ('Place in ' + args.context).ljust(45) + iam \
                + getattr(dpi, 'rh')['population'].rjust(20) + iam \
                + getattr(dpi, 'rh')[comp_name].rjust(20)
        else:
            return iam + 'Place'.ljust(45) + iam \
                + getattr(dpi, 'rh')['population'].rjust(20) + iam \
                + getattr(dpi, 'rh')[comp_name].rjust(20)[:20]

    # Print a row
    def sl_print_row(dpi):
        return iam + getattr(dpi, 'name').ljust(45)[:45] + iam \
               + getattr(dpi, 'fc')['population'].rjust(20) + iam \
               + getattr(dpi, print_)[comp_name].rjust(20)
    
    # Remove numpy.nans because they interfere with sorted()
    no_nans = list(filter(lambda x: not \
        numpy.isnan(getattr(x, sort_by)[comp_name]), d['demographicprofiles']))

    # If there's a filter pop, remove all places underneath it.
    if args.pop_filter:
        no_nans = list(filter(lambda x: \
        getattr(x, 'rc')['population'] >= args.pop_filter, no_nans))

    # If there's a filter_state, remove all places outside that county.
    if args.context:
        no_nans = list(filter(lambda x: \
        getattr(x, 'state') == args.context, no_nans))

    # For the median_year_structure_built component, remove values of zero and
    # 18...
    if args.comp_name == 'median_year_structure_built':
        no_nans = list(filter(lambda x: not \
        getattr(x, 'rc')['median_year_structure_built'] == 0, no_nans))
        no_nans = list(filter(lambda x: not \
        getattr(x, 'rc')['median_year_structure_built'] == 18, no_nans))

    # Sort our DemographicProfile instances by component or compound specified.
    sls = sorted(no_nans, key=lambda x: \
        getattr(x, sort_by)[comp_name], reverse=(not anti))

    # Print the header and places with their information.
    print(divider())
    print(sl_print_headers(d['demographicprofiles'][0]))
    print(divider())
    for sl in sls[:30]:
        print(sl_print_row(sl))
    print(divider())

def antisuperlatives(args):
    '''Wrapper function for antisuperlatives.'''
    superlatives(args, anti=True)

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

# View subparser
# Create parsors for the view command command
# DemographicProfiles #########################################################
dp_parsor = view_subparsers.add_parser('dp',
    description='View a DemographicProfile.')
dp_parsor.add_argument('census_place_string', help='the exact place name')
dp_parsor.set_defaults(func=get_dp)

# PlaceVectors ################################################################
pv_parsor = view_subparsers.add_parser('pv',
    description='View PlaceVectors nearest to a PlaceVector.')
pv_parsor.add_argument('census_place_string', help='the exact place name')
pv_parsor.add_argument('-p', '--pop_filter', help='filter by population')
pv_parsor.add_argument('-c', '--context', help='state to compare with')
pv_parsor.set_defaults(func=compare_placevectors)

# PlaceVectorApps #############################################################
pva_parsor = view_subparsers.add_parser('pva',
    description='View PlaceVectorApps nearest to a PlaceVectorApp')
pva_parsor.add_argument('census_place_string', help='the exact place name')
pva_parsor.add_argument('-p', '--pop_filter', help='filter by population')
pva_parsor.add_argument('-c', '--context', help='state to compare with')
pva_parsor.set_defaults(func=compare_placevectorapps)

# Superlatives ################################################################
sl_parsor = view_subparsers.add_parser('sl',
    description='View places that rank highest with regard to a certain characteristic.')
sl_parsor.add_argument('comp_name', help='the comp that you want to rank')
sl_parsor.add_argument('data_type', help='whether comp is a component or a compound')
sl_parsor.add_argument('-p', '--pop_filter', help='filter by population')
sl_parsor.add_argument('-c', '--context', help='use geographies within state')
sl_parsor.set_defaults(func=superlatives)

# Antisuperlatives ############################################################
asl_parsor = view_subparsers.add_parser('asl',
    description='View places that rank lowest with regard to a certain characteristic.')
asl_parsor.add_argument('comp_name', help='the comp that you want to rank')
asl_parsor.add_argument('data_type', help='whether comp is a component or a compound')
asl_parsor.add_argument('-p', '--pop_filter', help='filter by population')
asl_parsor.add_argument('-c', '--context', help='use geographies within state')
asl_parsor.set_defaults(func=antisuperlatives)

# Parse arguments
args = parser.parse_args()
args.func(args)
