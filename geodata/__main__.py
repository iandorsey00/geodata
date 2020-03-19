from database.Database import Database

import argparse
import sys
import numpy
import pickle

from tools.geodata_typecast import gdt, gdtf, gdti

from tools.StateTools import StateTools
from tools.CountyTools import CountyTools
from tools.KeyTools import KeyTools

import time

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

def compare_geovectors(args, mode='std'):
    '''Compare GeoVectors.'''
    d = initalize_database()

    st = d['st']
    ct = d['ct']
    kt = d['kt']

    # Split the geos with a pipe
    geo_split = args.display_label.split('|')
    search_name = geo_split[0]
    summary_level = '160'

    if args.context:
        if ':' in args.context:
            summary_level = '050'
        else:
            summary_level = '040'
    
    pv_list = d['geovectors']

    # Obtain the GeoVector for which we entered a name.
    comparison_pv = \
        list(filter(lambda x: x.name == search_name, pv_list))[0]

    # Filter by arguments:
    if summary_level == '050':
        key = 'us:' + args.context + '/county'
        county_name = kt.key_to_county_name[key]
        county_geoid = ct.county_name_to_geoid[county_name]

        pv_list = list(filter(lambda x: \
        county_geoid in getattr(x, 'counties'), pv_list))
    elif summary_level == '040':
        pv_list = list(filter(lambda x: x.state == args.context,
                            pv_list))

    # Population
    if args.pop_filter:
        pop_filter = gdt(args.pop_filter)
        pv_list = list(filter(lambda x: gdti(x.d['population']) > pop_filter,
                            pv_list))

    # Get the closest GeoVectors.
    # In other words, get the most demographically similar places.
    closest_pvs = sorted(pv_list,
        key=lambda x: comparison_pv.distance(x, mode=mode))[:6]

    print("The most demographically similar places are:")
    print()
    if mode == 'std':
        print('GEOGRAPHY'.ljust(40), 'COUNTY'.ljust(20), 'PDN', 'PCI', 'WHT', 'BLK', 'ASN', 'HPL', 'BDH', 'GDH', ' DISTANCE')
    elif mode == 'app':
        print('GEOGRAPHY'.ljust(40), 'COUNTY'.ljust(20), 'PDN', 'PCI', 'MYS', ' DISTANCE')

    # Print these GeoVectors
    for closest_pv in closest_pvs:
        print(closest_pv.display_row(mode), comparison_pv.distance(closest_pv, mode=mode))

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
    d = initalize_database()

    st = d['st']
    ct = d['ct']
    kt = d['kt']

    summary_level = '160'

    if args.context:
        if ':' in args.context:
            summary_level = '050'
        else:
            summary_level = '040'

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
    
    # Remove numpy.nans because they interfere with sorted()
    dpi_instances = list(filter(lambda x: not \
        numpy.isnan(getattr(x, sort_by)[comp_name]), d['demographicprofiles']))

    # If there's a filter pop, remove all places underneath it.
    if args.pop_filter:
        dpi_instances = list(filter(lambda x: \
        getattr(x, 'rc')['population'] >= args.pop_filter, dpi_instances))

    # Filter by state
    if summary_level == '040':
        dpi_instances = list(filter(lambda x: \
        getattr(x, 'state') == args.context, dpi_instances))
    # Filter by county
    elif summary_level == '050':
        key = 'us:' + args.context + '/county'
        county_name = kt.key_to_county_name[key]
        county_geoid = ct.county_name_to_geoid[county_name]

        dpi_instances = list(filter(lambda x: \
        county_geoid in getattr(x, 'counties'), dpi_instances))


    # For the median_year_structure_built component, remove values of zero and
    # 18...
    if args.comp_name == 'median_year_structure_built':
        dpi_instances = list(filter(lambda x: not \
        getattr(x, 'rc')['median_year_structure_built'] == 0, dpi_instances))
        dpi_instances = list(filter(lambda x: not \
        getattr(x, 'rc')['median_year_structure_built'] == 18, dpi_instances))

    # Sort our DemographicProfile instances by component or compound specified.
    sls = sorted(dpi_instances, key=lambda x: \
        getattr(x, sort_by)[comp_name], reverse=(not anti))

    # helper methods for printing (a)sl rows ##################################

    # The inter-area margin to divide display sections
    iam = ' '

    def divider(dpi):
        '''Print a divider for DemographicProfiles'''
        if args.comp_name == 'population':
            return '-' * 68
        else:
            return '-' * 89

    # dpi = demographicprofile_instance
    def sl_print_headers(dpi):
        '''Print a header for DemographicProfiles'''
        # Places
        if summary_level == '160':
            out_str = iam + 'Place'.ljust(45) + iam \
            + getattr(dpi, 'rh')['population'].rjust(20)
            # Print another column if the comp_name isn't population
            if args.comp_name != 'population':
                out_str += iam + getattr(dpi, 'rh')[comp_name].rjust(20)
            return out_str
        # State context
        elif summary_level == '040' or summary_level == '050':
            geography = ''

            if summary_level == '040':
                geography = st.get_name(args.context)
            else: # summary_level == '050':
                geography = county_name
            
            out_str = iam + ('Place in ' \
                + geography).ljust(45)[:45] + iam \
                + getattr(dpi, 'rh')['population'].rjust(20)

            # Print another column if the comp_name isn't population
            if args.comp_name != 'population':
                out_str += iam + getattr(dpi, 'rh')[comp_name].rjust(20)
            return out_str

    # dpi = demographicprofile_instance
    def sl_print_row(dpi):
        '''Print a data row for DemographicProfiles'''
        out_str = iam + getattr(dpi, 'name').ljust(45)[:45] + iam \
                  + getattr(dpi, 'fc')['population'].rjust(20)
        if args.comp_name != 'population':
            out_str += iam + getattr(dpi, print_)[comp_name].rjust(20)
        return out_str

    # Printing ################################################################

    # Print the header and places with their information.
    dpi = d['demographicprofiles'][0]
    print(divider(dpi))
    print(sl_print_headers(dpi))
    print(divider(dpi))
    for sl in sls[:30]:
        print(sl_print_row(sl))
    print(divider(dpi))

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
dp_parsor.add_argument('display_label', help='the exact place name')
dp_parsor.set_defaults(func=get_dp)

# GeoVectors [standard mode] ##################################################
gv_parsor = view_subparsers.add_parser('gv',
    description='View GeoVectors nearest to a GeoVector.')
gv_parsor.add_argument('display_label', help='the exact place name')
gv_parsor.add_argument('-p', '--pop_filter', help='filter by population')
gv_parsor.add_argument('-c', '--context', help='state to compare with')
gv_parsor.set_defaults(func=compare_geovectors)

# GeoVectors [appearance mode] ################################################
gva_parsor = view_subparsers.add_parser('gva',
    description='View GeoVectors nearest to a GeoVector [appearance mode]')
gva_parsor.add_argument('display_label', help='the exact place name')
gva_parsor.add_argument('-p', '--pop_filter', help='filter by population')
gva_parsor.add_argument('-c', '--context', help='state to compare with')
gva_parsor.set_defaults(func=compare_geovectors_app)

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
