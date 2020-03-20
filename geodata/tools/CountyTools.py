'''
Tools to find out what county/ies contain a place and vice versa. Also helps
with converting county GEOIDs to names.

Gets previously generated data to improve performance.
'''

from tools.data.county_geoid_to_name import county_geoid_to_name
from tools.data.county_name_to_geoid import county_name_to_geoid
from tools.data.county_names import county_names
from tools.data.county_to_places import county_to_places
from tools.data.place_to_counties import place_to_counties

class CountyTools:
    def __init__(self):
        self.county_geoid_to_name = county_geoid_to_name
        self.county_name_to_geoid = county_name_to_geoid
        self.county_names = county_names
        self.county_to_places = county_to_places
        self.place_to_counties = place_to_counties
