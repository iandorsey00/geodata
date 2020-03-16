'''
Transforms place name strings to consistent hashes.

The challenge for joining data for geographies from different datasets is
that standarized identifiers are not necessarily provided. For example, the
the city of Adelanto in California might be identified as "Adelanto" in one
source, "Adelanto, CA" in other, "Adelanto city, California" in still
another, and "Adelanto, California" in yet another. This leaves us with
nothing to join the data together.

This file attempts to offer a solution to this problem through a function
gives all place names a common identifier.

For example, "Adelanto, California" will be hashed as "us:ca:adelanto".
'''

# A dictionary of states mapped to their lowercase abbreviations.
states = {
    'Alaska': 'ak',
    'Alabama': 'al',
    'Arkansas': 'ar',
    'American Samoa': 'as',
    'Arizona': 'az',
    'California': 'ca',
    'Colorado': 'co',
    'Connecticut': 'ct',
    'District of Columbia': 'dc',
    'Delaware': 'de',
    'Florida': 'fl',
    'Georgia': 'ga',
    'Guam': 'gu',
    'Hawaii': 'hi',
    'Iowa': 'ia',
    'Idaho': 'id',
    'Illinois': 'il',
    'Indiana': 'in',
    'Kansas': 'ks',
    'Kentucky': 'ky',
    'Louisiana': 'la',
    'Massachusetts': 'ma',
    'Maryland': 'md',
    'Maine': 'me',
    'Michigan': 'mi',
    'Minnesota': 'mn',
    'Missouri': 'mo',
    'Northern Mariana Islands': 'mp',
    'Mississippi': 'ms',
    'Montana': 'mt',
    'National': 'na',
    'North Carolina': 'nc',
    'North Dakota': 'nd',
    'Nebraska': 'ne',
    'New Hampshire': 'nh',
    'New Jersey': 'nj',
    'New Mexico': 'nm',
    'Nevada': 'nv',
    'New York': 'ny',
    'Ohio': 'oh',
    'Oklahoma': 'ok',
    'Oregon': 'or',
    'Pennsylvania': 'pa',
    'Puerto Rico': 'pr',
    'Rhode Island': 'ri',
    'South Carolina': 'sc',
    'South Dakota': 'sd',
    'Tennessee': 'tn',
    'Texas': 'tx',
    'Utah': 'ut',
    'Virginia': 'va',
    'Virgin Islands': 'vi',
    'Vermont': 'vt',
    'Washington': 'wa',
    'Wisconsin': 'wi',
    'West Virginia': 'wv',
    'Wyoming': 'wy'
}

# Define hardcoded hashes for exceptionally tricky geographic names.
hardcoded_values = {
    # Official name of Ventura is San Buenaventura. The official name is not
    # used much outside of formal settings.
    "San Buenaventura (Ventura) city, California" : "us:ca:ventura",
    # The same for Paso Robles.
    "El Paso de Robles (Paso Robles) city, California" : "us:ca:pasorobles",

    # Green Acres CDP, California and Greenacres CDP, California differ only by
    # a space. They are in Riverside and Kern counties, respectively.
    "Green Acres CDP, California" : "us:ca:greenacres/cdp/riverside",
    "Greenacres CDP, California" : "us:ca:greenacres/cdp/kern",

    # There are two places in the U.S. with a comma in the name.
    # We'll have to hardcode them right now.
    "Islamorada, Village of Islands village; Florida" : 'us:fl:islamorada',
}

# For the time being, we will pass in arguments for the country and the
# state/province.
def key_hash(unhashed_string, country="us"):
    # First of all, if the value is hardcoded, skip everything and return the
    # hardcoded value.
    if unhashed_string in hardcoded_values:
        return hardcoded_values[unhashed_string]

    # The beginning of the hashed string
    hashed_string = country + ':'

    # Declare a boolean which specifies whether the geography is a CDP.
    cdp = False

    # First of all, if the geography names contain a comma, split it on the
    # comma.
    comma_split = unhashed_string.split(", ")
    # Get the first item
    comma_split_first_item = comma_split[0]
    # Get the last item, the state.
    state = comma_split[-1]
    # Transform the long state name into its lowercase abbreviation.
    try:
        state = states[state]
    except KeyError:
        print(unhashed_string)
    # Add it to the output string
    hashed_string += state + ':'

    # Determine whether a geography is a CDP.
    if "CDP" in comma_split_first_item:
        cdp = True

    # Remove unwanted words
    cdp_removed = comma_split_first_item.replace('CDP', '')
    city_removed = cdp_removed.replace('city', '')
    town_removed = city_removed.replace('town', '')

    # Remove whitespace
    whitespace_removed = city_removed.replace(' ', '')

    # Remove hyphens or dashes
    dashes_removed = whitespace_removed.replace('-', '')

    # To lower case
    lowercase = whitespace_removed.lower()

    # If the place is a CDP, attach the /cdp option.
    if cdp:
        hashed_string += lowercase + "/cdp"
    # Otherwise, we're done.
    else:
        hashed_string += lowercase

    return hashed_string
