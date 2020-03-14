from database import Database
import getopt
import sys
import pickle
import numpy
from geodata_typecast import gdt, gdtf, gdti

# Display help information.
def display_help():
    '''Print the help screen.'''
    # print('Basic usage:       geodata option')
    # print('Options:')
    # print()
    # print('  -h|--help                              Display this information.')
    # print('  -c|--create-database                   Create a new database.')
    # print()
    # print('PlaceVector usage: geodata -p|-a pv_query')
    # print('PlaceVector usage: geodata --placevectors=pv_query')
    # print('PlaceVector usage: geodata --placevectorapps=pv_query')
    # print()
    # print('Options:')
    # print()
    # print('  -p pv_query|--placevectors=pv_query    Compare PlaceVectors.')
    # print('  -a pv_query|--placevectorapps=pv_query Compare PlaceVectorApps.')
    # print()
    # print('pv_query: PlaceVector queries')
    # print()
    # print('    "place[|county]"')
    # print()
    # print('Compare the PlaceVector associated with place (required) with')
    # print('PlaceVectors in county (optional). If county is not specified,')
    # print('Compare the PlaceVector with all others in the state.')
    # print()
    # print('In each case, the closest PlaceVectors will be printed.')
    # print()
    # print('Example: geodata -p "Los Angeles city, California"')
    # print('         Get the closest PlaceVectors to Los Angeles, CA.')
    # print()
    # print('Example: geodata -a "San Diego city, California|Los Angeles County"')
    # print('         Get the closest PlaceVectorsApps to San Diego, CA in Los')
    # print('         Angeles County, CA.')
    # print()
    # print('DemographicProfile usage: geodata -d "place_str"')
    # print('DemographicProfile usage: geodata --demographicprofile="place_str"')
    # print()
    # print('Get the DemographicProfile for a place.')
    # print()
    # print('Example: geodata -d "San Francisco city, California"')
    # print('         Get the DemographicProfile for San Francisco, CA.')
    # print()
    # print('Superlative usage:     geodata -s "superlative_query"')
    # print('Superlative usage:     geodata --superlative="superlative_query"')
    # print('Antisuperlative usage: geodata -n "superlative_query"')
    # print('Antisuperlative usage: geodata -antisuperlative="superlative_query"')
    # print()
    # print('Print the top (or bottom) 30 places with by component or compound')
    # print('value.')
    # print()
    # print('superlative_query')
    # print()
    # print('    comp_name:c|cc[:filter_pop[:filter_county]]')
    # print()
    # print('See documentation.')
    # print()
    # print('Example: geodata -s "per_capita_income:c:50000"')
    # print('         Get the top 30 places in California by per capita income')
    # print('         with a population of over 50,000.')
    # print()
    # print('Example: geodata -n "bachelors_degree_or_higher:cc:0:Orange County"')
    # print('         Get the bottom 30 places in California by percent of the')
    # print("         population over 25 with a bachelor's degree or higher in")
    # print('         Orange County.')
    print('Usage:')
    print('  geodata (ld|loaddata) ...')
    print('  geodata (db|database) ...')
    print('  geodata (v|view) ...')
    print('  (For each command above, use -h or --help for more information.)')
    print('  geodata -h | --help')
    print('  geodata -v | --version')
    print()
    print('Options:')
    print('  -h --help     Show this screen.')
    print('  -v --version  Show version.')

# Create and save a database.
def create_database():
    pickle.dump(Database(), open('./bin/default.db', 'wb'))

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
    
# Process options and arguments.
try:
    opts, args = getopt.getopt(sys.argv[1:],
                               'hcp:a:d:s:n:',
                               ['help', 'create-database', 'placevectors=',
                               'placevectorapps=', 'demographicprofile=',
                               'superlatives=', 'antisuperlatives='])
# If there was an error with processing arguments, display help information,
# then exit.
except getopt.GetoptError:
    display_help()
    sys.exit(2)

# Determine what to do based on command line args.
for opt, arg in opts:
    # Basics ##################################################################
    # Display help.
    if   opt in ('-h', '--help'):
        display_help()
        sys.exit(0)
    # Create a database.
    elif opt in ('-c', '--create-database'):
        create_database()
        sys.exit(0)

    # PlaceVectors ############################################################
    # Compare PlaceVectors
    elif opt in ('-p', '--placevectors'):
        compare_placevectors(arg)
        sys.exit(0)
    # Compare PlaceVectorApps
    elif opt in ('-a', '--placevectorapps'):
        compare_placevectors(arg, 'placevectorapp')
        sys.exit(0)

    # DemographicProfiles #####################################################
    elif opt in ('-d', '--demographicprofile'):
        get_dp(arg)
        sys.exit(0)

    # Superlatives and antisuperlatives #######################################
    elif opt in ('-s', '--superlatives'):
        superlatives(arg)
        sys.exit(0)
    elif opt in ('-n', '--antisuperlatives'):
        superlatives(arg, anti=True)
        sys.exit(0)

# Currently, this app compares PlaceVectors by default.
compare_placevectors()
