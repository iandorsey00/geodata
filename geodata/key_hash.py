#
# key_hash.py
#
# Transforms place name strings to consistent hashes.
#
# The challenge for joining data for geographies from different datasets is
# that standarized identifiers are not necessarily provided. For example, the
# the city of Adelanto in California might be identified as "Adelanto" in one
# source, "Adelanto, CA" in other, "Adelanto city, California" in still
# another, and "Adelanto, California" in yet another. This leaves us with
# nothing to join the data together.
#
# This file attempts to offer a solution to this problem through a function
# gives all place names a common identifier.
#
# For example, "Adelanto, California" will be hashed as "us:ca:adelanto".
#
# At this point, we will focus on geographies in California.
#

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
    "Greenacres CDP, California" : "us:ca:greenacres/cdp/kern"
}

# For the time being, we will pass in arguments for the country and the
# state/province.
def key_hash(unhashed_string, country="us", state_province="ca"):
    # First of all, if the value is hardcoded, skip everything and return the
    # hardcoded value.
    if unhashed_string in hardcoded_values:
        return hardcoded_values[unhashed_string]

    # Because we'll only be hashing geographies in California for now, start
    # the string out with "us:ca:".
    hashed_string = "us:ca:"

    # Declare a boolean which specifies whether the geography is a CDP.
    cdp = False

    # First of all, if the geography names contain a comma, split it on the
    # comma.
    comma_split = unhashed_string.split(", ")
    # Discard portion after the comma.
    comma_split_first_item = comma_split[0]

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
