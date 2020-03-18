'''
Tools to find out what county/ies contain a place and vice versa. Also helps
with converting county GEOIDs to names.
'''
from tools.StateTools import StateTools
from collections import defaultdict
import csv

class CountyTools:
    def get_geo_csv_rows(self):
        '''Get all rows geographic CSV files for every state'''
        st = StateTools()
        # Get rows from CSV
        rows = []
        # Get rows from CSV files for each state.
        for state in st.get_abbrevs(lowercase=True):
            this_path = self.path + 'g20185' + state + '.csv'
            with open(this_path, 'rt', encoding='iso-8859-1') as f:
                rows += list(csv.reader(f))
        
        return rows

    def __init__(self, path):
        self.path = path

        # place_to_counties ###################################################
        # Convert a place GEOID to a list of corresponding county GEOIDs.
        # Usually, a place is fully contained within a county. But's not
        # *always* the case.
        self.place_to_counties = defaultdict(list)

        # Get rows from CSV
        rows = self.get_geo_csv_rows()
                
        # Filter for summary level code 155 (State-Place-Counties)
        rows = list(filter(lambda x: x[2] == '155', rows))

        for row in rows:
            self.place_to_counties[row[48][7:14]].append(row[48][7:9] + row[48][14:])
                                    # place GEOID         # county GEOID

        # county_geoid_to_name ################################################
        # Convert a place GEOID to a list of corresponding county GEOIDs.
        # Usually, a place is fully contained within a county. But's not
        # *always* the case.
        self.county_geoid_to_name = dict()

        # Get rows from CSV
        rows = self.get_geo_csv_rows()
                
        # Filter for summary level code 050 (State-Counties)
        rows = list(filter(lambda x: x[2] == '050', rows))

        for row in rows:
            self.county_geoid_to_name[row[48][7:]] = row[49]

        # county_to_places ####################################################
        # Convert a county GEOID to a list of the place GEOIDs it contains.
        self.county_to_places = defaultdict(list)

        # Just filp self.place_to_counties
        for key, values in self.place_to_counties.items():
            for value in values:
                self.county_to_places[value].append(key)

        # Remove duplicate values
        for key, values in self.county_to_places.items():
            self.county_to_places[key] = list(dict.fromkeys(values))
