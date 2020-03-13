from Database import Database
import getopt
import sys
import pickle

# Display help information.
def display_help():
    print('Usage: geodata [option]')
    print('Options:')
    print('  -h|--help             Display this information.')
    print('  -c|--create-database  Create a new database.')
    print('  -p|--placevectors     Compare PlaceVectors.')
    print('  -a|--placevectorapps  Compare PlaceVectorApps.')

# Create and save a database.
def create_database():
    pickle.dump(Database(), open('../bin/default.db', 'wb'))

# Load a database.
def load_database():
    with open('../bin/default.db', 'rb') as f:
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
def compare_placevectors(type='placevector'):
    d = initalize_database()

    if type == 'placevector':
        pv_list = d.placevectors
    elif type == 'placevectorapp':
        pv_list = d.placevectorapps

    print()
    search_name = input("Enter the name of a place that you want to compare with others: ")
    filter_county = input("Would you like to filter by a county? If not, just press Enter: ")
    print()

    # Obtain the PlaceVector for which we entered a name.
    comparison_pv = \
        list(filter(lambda x: x.name == search_name, pv_list))[0]

    print("The most demographically similar places are:")
    print()

    # Filter by county if a filter_county was specified.
    if filter_county != '':
        filtered_pvs = list(filter(lambda x: x.county == filter_county,
                            pv_list))

    # Get the closest PlaceVectors.
    # In other words, get the most demographically similar places.
    closest_pvs = sorted(filtered_pvs,
        key=lambda x: comparison_pv.distance(x))[:6]

    # Print these PlaceVectors
    for closest_pv in closest_pvs:
        print(closest_pv)

# Process options and arguments.
try:
    opts, args = getopt.getopt(sys.argv[1:],
                               'hcpa',
                               ['help', 'create-database', 'placevectors',
                               'placevectorapps'])
# If there was an error with processing arguments, display help information,
# then exit.
except getopt.GetoptError:
    display_help()
    sys.exit(2)

# Determine what to do based on command line args.
for opt, arg in opts:
    # Display help.
    if   opt in ('-h', '--help'):
        display_help()
        sys.exit(0)
    # Create a database.
    elif opt in ('-c', '--create-database'):
        create_database()
        sys.exit(0)
    # Compare PlaceVectors
    elif opt in ('-p', '--placevectors'):
        compare_placevectors()
        sys.exit(0)
    # Compare PlaceVectors
    elif opt in ('-a', '--placevectorapps'):
        compare_placevectors('placevectorapp')
        sys.exit(0)

# Currently, this app compares PlaceVectors by default.
compare_placevectors()
