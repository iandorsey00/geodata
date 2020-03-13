#
# DemographicProfile.py
#
# A set of components intended to describe a specific geography or compare
# small numbers of geographies.
#

from geodata_typecast import gdt, gdti, gdtf

class DemographicProfile:
    '''Used to display data for a geography.'''
    def __init__(self, geo_instance):

        self.name = geo_instance.name
        self.county = geo_instance.county
        self.key = geo_instance.key
        self.data = geo_instance.data
        self.geoheader = geo_instance.geoheader

        #######################################################################
        # Row headers - Row labels

        self.rh = dict()

        # Population category
        self.rh['population'] = 'Total population'
        self.rh['population_density'] = 'Population density'

        # Geographic category
        self.rh['land_area'] = 'Land area (in square miles)'

        # Race category
        self.rh['white_alone'] = '    White alone'
        self.rh['black_alone'] = '    Black alone'
        self.rh['asian_alone'] = '    Asian alone'
        self.rh['other_race']  = '    Other'
        # Technically not a race, but included in the race category
        self.rh['hispanic_or_latino'] = '    Hispanic or Latino'

        # Education category
        self.rh['population_25_years_and_older'] = 'Total population 25 years and older'
        self.rh['bachelors_degree_or_higher'] = "  Bachelor's degree or higher"
        self.rh['graduate_degree_or_higher'] =  '  Graduate degree or higher'

        # Income category
        self.rh['per_capita_income'] = 'Per capita income'

        # Housing category
        self.rh['median_year_structure_built'] = 'Median year unit built'
        self.rh['median_value'] = 'Median value'
        self.rh['median_rent'] = 'Median rent'

        #######################################################################
        # Raw components - Data that comes directly from the Census data files
        self.rc = dict()

        # Population category
        self.rc['population'] = gdt(self.data.B01003_1)

        # Geographic category
        self.rc['land_area'] = gdtf(self.geoheader.ALAND_SQMI)

        # Race category
        self.rc['white_alone'] = gdt(self.data.B02001_2)
        self.rc['black_alone'] = gdt(self.data.B02001_3)
        self.rc['asian_alone'] = gdt(self.data.B02001_5)
        self.rc['other_race'] = gdt(self.data.B01003_1) \
            - gdt(self.data.B02001_2) - gdt(self.data.B02001_3) \
            - gdt(self.data.B02001_5)
        # Technically not a race, but included in the race category
        self.rc['hispanic_or_latino'] = gdt(self.data.B03002_12)

        # Education category
        self.rc['population_25_years_and_older'] = gdt(self.data.B15003_1)
        self.rc['bachelors_degree_or_higher'] = gdt(self.data.B15003_22) \
            + gdt(self.data.B15003_23) + gdt(self.data.B15003_24) \
            + gdt(self.data.B15003_25)
        self.rc['graduate_degree_or_higher'] = gdt(self.data.B15003_23) \
           + gdt(self.data.B15003_24) + gdt(self.data.B15003_25)

        # Income category
        self.rc['per_capita_income'] = gdt(self.data.B19301_1)

        # Housing category
        self.rc['median_year_structure_built'] = gdt(self.data.B25035_1)
        self.rc['median_value'] = gdt(self.data.B25077_1)
        self.rc['median_rent'] = gdt(self.data.B25058_1)

        #######################################################################
        # Formatted components: Thousands seperaters, dollar signs, etc.
        self.fc = dict()

        for key in self.rc.keys():
            if key not in ['per_capita_income', 'median_year_structure_built',
                'median_value', 'median_rent', 'land_area']:
                self.fc[key] = f'{self.rc[key]:,}'
            elif key not in ['median_year_structure_built', 'land_area']:
                self.fc[key] = '$' + f'{self.rc[key]:,}'
            elif key == 'land_area':
                self.fc[key] = f'{self.rc[key]:,.1f}'
            else: # key == 'median_year_structure_built'
                self.fc[key] = self.rc[key]

        #######################################################################
        # Compounds: The result of mathematic operations of raw components.
        # Often, they are the result of the data they represent divided by
        # their universes.

        self.c = dict()

        # Population category
        self.c['population_density'] = self.rc['population'] / self.rc['land_area']

        # Geographic category
        # No compound for this category.

        # Race category - Percentages of the total population
        self.c['white_alone'] = self.rc['white_alone'] / self.rc['population'] * 100.0
        self.c['black_alone'] = self.rc['asian_alone'] / self.rc['population'] * 100.0
        self.c['asian_alone'] = self.rc['black_alone'] / self.rc['population'] * 100.0
        self.c['other_race'] = self.rc['other_race'] / self.rc['population'] * 100.0
        # Technically not a race, but included in the race category
        self.c['hispanic_or_latino'] = self.rc['hispanic_or_latino'] / self.rc['population'] * 100.0

        # Education category - Percentages of the population 25 years and older
        self.c['bachelors_degree_or_higher'] = self.rc['bachelors_degree_or_higher'] / self.rc['population_25_years_and_older'] * 100.0
        self.c['graduate_degree_or_higher'] = self.rc['graduate_degree_or_higher'] / self.rc['population_25_years_and_older'] * 100.0

        # Income category
        # No compounds for this category

        # Housing category
        # No compounds for this category

        #######################################################################
        # Formatted compounds: The result of mathematic operations of raw
        # components
        
        self.fcd = dict()

        for key in self.c.keys():
            if key == 'population_density':
                self.fcd[key] = f'{self.c[key]:,.1f}' + '/sqmi'
            else:
                self.fcd[key] = f'{self.c[key]:,.1f}' + '%'

        #######################################################################
        # Inter-area margin (for display purposes)
        self.iam = ' '

    def __repr__(self):
        return "DemographicProfile(key='%s', name='%s', county='%s')" % (
            self.key, self.name, self.county)

    def dp_full_row_str(self, content):
        return self.iam + content.ljust(54) + self.iam + '\n'

    def divider(self):
        return '-' * 56 + '\n'

    def blank_line(self):
        return '\n'
    
    def dp_row_str(self, record_col, component_col, compound_col):
        return self.iam + record_col.ljust(30) + self.iam \
            + component_col.rjust(11) + self.iam + compound_col.rjust(11) \
            + self.iam + '\n'

    def __str__(self):
        return self.divider() \
             + self.dp_full_row_str(self.name) \
             + self.dp_full_row_str(self.county) \
             + self.dp_full_row_str(self.key) \
             + self.divider() \
             + self.dp_full_row_str('POPULATION') \
             + self.dp_row_str(self.rh['population'], '', self.fc['population']) \
             + self.dp_row_str(self.rh['population_density'], '', self.fcd['population_density']) \
             + self.dp_full_row_str('  Race') \
             + self.dp_row_str(self.rh['white_alone'], self.fc['white_alone'], self.fcd['white_alone']) \
             + self.dp_row_str(self.rh['black_alone'], self.fc['black_alone'], self.fcd['black_alone']) \
             + self.dp_row_str(self.rh['asian_alone'], self.fc['asian_alone'], self.fcd['asian_alone']) \
             + self.dp_row_str(self.rh['other_race'], self.fc['other_race'], self.fcd['other_race']) \
             + self.dp_full_row_str('  Hispanic or Latino (of any race') \
             + self.dp_row_str(self.rh['hispanic_or_latino'], self.fc['hispanic_or_latino'], self.fcd['hispanic_or_latino']) \
             + self.divider()

