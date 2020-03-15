from database.Database import Database
import argparse
import sys
import pickle
import numpy
from geodata_typecast import gdt, gdtf, gdti

# Create and save a database.
def create_database(args):
    pickle.dump(Database(args.path), open('./bin/default.db', 'wb'))

# Load a database.
def load_database():
    with open('./bin/default.db', 'rb') as f:
        return pickle.load(f)

def initalize_database():
    # Try to open the default database, located at ../bin/default.db.
    try:
        d = load_database()
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
            create_database()
            d = load_database()
            return d
        # Otherwise, exit.
        else:
            sys.exit(0)

# Compare certain types of PlaceVectors.
# type options:
#   placevector         PlaceVector (default)
#   placevectorapp      PlaceVectorApp
def compare_placevectors(geo, type='placevector'):
    d = initalize_database()

    if type == 'placevector':
        pv_list = d.placevectors
    elif type == 'placevectorapp':
        pv_list = d.placevectorapps

    # Split the geos with a pipe
    geo_split = geo.split('|')

    search_name = geo_split[0]

    # See if the is a filter_county specified. If not, set it to an empty
    # string.
    if len(geo_split) > 1:
        filter_county = geo_split[1]
    else:
        filter_county = ''

    # Obtain the PlaceVector for which we entered a name.
    comparison_pv = \
        list(filter(lambda x: x.name == search_name, pv_list))[0]

    print("The most demographically similar places are:")
    print()

    # Filter by county if a filter_county was specified.
    if filter_county != '':
        filtered_pvs = list(filter(lambda x: x.county == filter_county,
                            pv_list))
    else:
        filtered_pvs = pv_list

    # Get the closest PlaceVectors.
    # In other words, get the most demographically similar places.
    closest_pvs = sorted(filtered_pvs,
        key=lambda x: comparison_pv.distance(x))[:6]

    # Print these PlaceVectors
    for closest_pv in closest_pvs:
        print(closest_pv)
        print("Distance:", comparison_pv.distance(closest_pv))

# Get DemographicProfiles
def get_dp(place):
    d = initalize_database()

    dp = list(filter(lambda x: x.name == place, d.demographicprofiles))[0]
    print(str(dp))

# Superlatives and antisuperlatives
def superlatives(arg, anti=False):
    d = initalize_database()

    # Use the colon (:) to seperate subargs
    filter_str = ':'
    # Determine how many args
    args = len(arg.split(filter_str))

    # Assign comp_name (component_name), data_type, filter_pop, and
    # filter_county based on position and arg count
    if args == 2:
        comp_name, data_type = arg.split(filter_str)
        filter_pop = None
        filter_county = None
    elif args == 3:
        comp_name, data_type, filter_pop = arg.split(filter_str)
        filter_county = None
    elif args == 4:
        comp_name, data_type, filter_pop, filter_county = arg.split(filter_str)

    # If a filter_pop was specified, parse it.
    if filter_pop:
        filter_pop = gdti(filter_pop)

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
        if filter_county:
            return iam + ('Place in ' + filter_county).ljust(45) + iam \
                + getattr(dpi, 'rh')['population'].rjust(20) + iam \
                + getattr(dpi, 'rh')[comp_name].rjust(20)
        else:
            return iam + 'Place'.ljust(45) + iam \
                + getattr(dpi, 'rh')['population'].rjust(20) + iam \
                + getattr(dpi, 'rh')[comp_name].rjust(20)

    # Print a row
    def sl_print_row(dpi):
        return iam + getattr(dpi, 'name').ljust(45) + iam \
               + getattr(dpi, 'fc')['population'].rjust(20) + iam \
               + getattr(dpi, print_)[comp_name].rjust(20)
    
    # Remove numpy.nans because they interfere with sorted()
    no_nans = list(filter(lambda x: not \
        numpy.isnan(getattr(x, sort_by)[comp_name]), d.demographicprofiles))

    # If there's a filter pop, remove all places underneath it.
    if filter_pop:
        no_nans = list(filter(lambda x: \
        getattr(x, 'rc')['population'] >= filter_pop, no_nans))

    # If there's a filter_county, remove all places outside that county.
    if filter_county:
        no_nans = list(filter(lambda x: \
        getattr(x, 'county') == filter_county, no_nans))

    # Sort our DemographicProfile instances by component or compound specified.
    sls = sorted(no_nans, key=lambda x: \
        getattr(x, sort_by)[comp_name], reverse=(not anti))

    # Print the header and places with their information.
    print(divider())
    print(sl_print_headers(d.demographicprofiles[0]))
    print(divider())
    for sl in sls[:30]:
        print(sl_print_row(sl))
    print(divider())
    
# # Process options and arguments.
# try:
#     opts, args = getopt.getopt(sys.argv[1:],
#                                'hcp:a:d:s:n:',
#                                ['help', 'create-database', 'placevectors=',
#                                'placevectorapps=', 'demographicprofile=',
#                                'superlatives=', 'antisuperlatives='])
# # If there was an error with processing arguments, display help information,
# # then exit.
# except getopt.GetoptError:
#     display_help()
#     sys.exit(2)

# # Determine what to do based on command line args.
# for opt, arg in opts:
#     # Basics ##################################################################
#     # Display help.
#     if   opt in ('-h', '--help'):
#         display_help()
#         sys.exit(0)
#     # Create a database.
#     elif opt in ('-c', '--create-database'):
#         create_database()
#         sys.exit(0)

#     # PlaceVectors ############################################################
#     # Compare PlaceVectors
#     elif opt in ('-p', '--placevectors'):
#         compare_placevectors(arg)
#         sys.exit(0)
#     # Compare PlaceVectorApps
#     elif opt in ('-a', '--placevectorapps'):
#         compare_placevectors(arg, 'placevectorapp')
#         sys.exit(0)

#     # DemographicProfiles #####################################################
#     elif opt in ('-d', '--demographicprofile'):
#         get_dp(arg)
#         sys.exit(0)

#     # Superlatives and antisuperlatives #######################################
#     elif opt in ('-s', '--superlatives'):
#         superlatives(arg)
#         sys.exit(0)
#     elif opt in ('-n', '--antisuperlatives'):
#         superlatives(arg, anti=True)
#         sys.exit(0)

# # Currently, this app compares PlaceVectors by default.
# compare_placevectors()

###############################################################################
# Argument parsing

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
createdb_parser.set_defaults(func=create_database)

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

# PlaceVectors ################################################################
pv_parsor = view_subparsers.add_parser('pv',
    description='View PlaceVectors nearest to a PlaceVector.')
pv_parsor.add_argument('census_place_string', help='the exact place name')
pv_parsor.add_argument('context', help='group to compare with')

# PlaceVectorApps #############################################################
pva_parsor = view_subparsers.add_parser('pva',
    description='View PlaceVectorApps nearest to a PlaceVectorApp')
pva_parsor.add_argument('census_place_string', help='the exact place name')
pva_parsor.add_argument('context', help='group to compare with')
sl_parsor = view_subparsers.add_parser('sl')
asl_parsor = view_subparsers.add_parser('asl')

args = parser.parse_args()
args.func(args)
