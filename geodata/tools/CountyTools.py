'''
Tools to find out what county/ies contain a place and vice versa. Also helps
with converting county GEOIDs to names.
'''
from tools.StateTools import StateTools
from tools.CSVTools import CSVTools
from collections import defaultdict
import csv

class CountyTools:
    def __init__(self, csvt_instance):
        # Get rows from CSV files
        rows = csvt_instance.rows

        # place_to_counties ###################################################
        # county_to_places ####################################################
        # Convert a place GEOID to a list of corresponding county GEOIDs.
        # Usually, a place is fully contained within a county. But's not
        # *always* the case.
        self.place_to_counties = defaultdict(list)
        self.county_to_places = defaultdict(list)
                
        # Filter for summary level code 155 (State-Place-Counties)
        these_rows = list(filter(lambda x: x[2] == '155', rows))

        for row in these_rows:
            place_geoid = row[48][7:14]
            county_geoid = row[48][7:9] + row[48][14:]

            self.place_to_counties[place_geoid].append(county_geoid)
            self.county_to_places[county_geoid].append(place_geoid)

        # Remove duplicate values
        for county, places in self.county_to_places.items():
            self.county_to_places[county] = list(dict.fromkeys(places))

        # county_geoid_to_name ################################################
        # county_name_to_geoid ################################################
        # county_names ########################################################
        # Convert a place GEOID to a list of corresponding county GEOIDs.
        # Usually, a place is fully contained within a county. But's not
        # *always* the case.
        self.county_geoid_to_name = dict()
        self.county_name_to_geoid = dict()
        self.county_names = []
                
        # Filter for summary level code 050 (State-Counties)
        these_rows = list(filter(lambda x: x[2] == '050', rows))

        for row in these_rows:
            county_geoid = row[48][7:]
            county_name = row[49]

            self.county_geoid_to_name[county_geoid] = county_name
            self.county_name_to_geoid[county_name] = county_geoid
            self.county_names.append(county_name)
