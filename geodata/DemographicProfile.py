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
        self.rc['population'] = gdt(geo_instance.data.B01003_1)

        # Geographic category
        self.rc['land_area'] = gdtf(geo_instance.geoheader.ALAND_SQMI)

        # Race category
        self.rc['white_alone'] = gdt(geo_instance.data.B02001_2)
        self.rc['black_alone'] = gdt(geo_instance.data.B02001_3)
        self.rc['asian_alone'] = gdt(geo_instance.data.B02001_5)
        self.rc['other_race'] = gdt(geo_instance.data.B01003_1) \
            - gdt(geo_instance.data.B02001_2) - gdt(geo_instance.data.B02001_3) \
            - gdt(geo_instance.data.B02001_5)
        # Technically not a race, but included in the race category
        self.rc['hispanic_or_latino'] = gdt(geo_instance.data.B03002_12)

        # Education category
        self.rc['population_25_years_and_older'] = gdt(geo_instance.data.B15003_1)
        self.rc['bachelors_degree_or_higher'] = gdt(geo_instance.data.B15003_22) \
            + gdt(geo_instance.data.B15003_23) + gdt(geo_instance.data.B15003_24) \
            + gdt(geo_instance.data.B15003_25)
        self.rc['graduate_degree_or_higher'] = gdt(geo_instance.data.B15003_23) \
           + gdt(geo_instance.data.B15003_24) + gdt(geo_instance.data.B15003_25)

        # Income category
        self.rc['per_capita_income'] = gdt(geo_instance.data.B19301_1)

        # Housing category
        self.rc['median_year_structure_built'] = gdt(geo_instance.data.B25035_1)
        self.rc['median_value'] = gdt(geo_instance.data.B25077_1)
        self.rc['median_rent'] = gdt(geo_instance.data.B25058_1)

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
                self.fc[key] = str(self.rc[key])

        #######################################################################
        # Compounds: The result of mathematic operations of raw components.
        # Often, they are the result of the data they represent divided by
        # their universes.

        # Most of the if/else statements below avoid division by zero errors.

        self.c = dict()

        if self.rc['land_area'] != 0:
            # Population category
            self.c['population_density'] = self.rc['population'] / self.rc['land_area']
        else:
            self.c['population_density'] = 0.0

        # Geographic category
        # No compound for this category.

        if self.rc['population'] != 0:
            # Race category - Percentages of the total population
            self.c['white_alone'] = self.rc['white_alone'] / self.rc['population'] * 100.0
            self.c['black_alone'] = self.rc['asian_alone'] / self.rc['population'] * 100.0
            self.c['asian_alone'] = self.rc['black_alone'] / self.rc['population'] * 100.0
            self.c['other_race'] = self.rc['other_race'] / self.rc['population'] * 100.0
            # Technically not a race, but included in the race category
            self.c['hispanic_or_latino'] = self.rc['hispanic_or_latino'] / self.rc['population'] * 100.0
        else:
            # Race category - Percentages of the total population
            self.c['white_alone'] = 0.0
            self.c['black_alone'] = 0.0
            self.c['asian_alone'] = 0.0
            self.c['other_race'] = 0.0          # Technically not a race, but included in the race category
            self.c['hispanic_or_latino'] = 0.0

        if self.rc['population_25_years_and_older'] != 0:
            # Education category - Percentages of the population 25 years and older
            self.c['population_25_years_and_older'] = self.rc['population_25_years_and_older'] / self.rc['population'] * 100.0
            self.c['bachelors_degree_or_higher'] = self.rc['bachelors_degree_or_higher'] / self.rc['population_25_years_and_older'] * 100.0
            self.c['graduate_degree_or_higher'] = self.rc['graduate_degree_or_higher'] / self.rc['population_25_years_and_older'] * 100.0
        else:
            self.c['population_25_years_and_older'] = 0.0
            self.c['bachelors_degree_or_higher'] = 0.0
            self.c['graduate_degree_or_higher'] = 0.0


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
        return '-' * 69 + '\n'

    def blank_line(self):
        return '\n'
    
    def dp_row_str(self, record_col, component_col, compound_col):
        return self.iam + record_col.ljust(35) + self.iam \
            + component_col.rjust(15) + self.iam + compound_col.rjust(15) \
            + self.iam + '\n'

    def dp_row_std(self, key):
        return self.dp_row_str(self.rh[key], self.fc[key], self.fcd[key])

    # For rows without a compound
    def dp_row_nc(self, key):
        return self.dp_row_str(self.rh[key], '', self.fc[key])

    def __str__(self):
        return self.divider() \
             + self.dp_full_row_str(self.name) \
             + self.dp_full_row_str(self.county) \
             + self.dp_full_row_str(self.key) \
             + self.divider() \
             + self.dp_full_row_str('POPULATION') \
             + self.dp_row_nc('population') \
             + self.dp_row_str(self.rh['population_density'], '', self.fcd['population_density']) \
             + self.dp_full_row_str('  Race') \
             + self.dp_row_std('white_alone') \
             + self.dp_row_std('black_alone') \
             + self.dp_row_std('asian_alone') \
             + self.dp_row_std('other_race') \
             + self.dp_full_row_str('  Hispanic or Latino (of any race)') \
             + self.dp_row_std('hispanic_or_latino') \
             + self.dp_full_row_str('EDUCATION') \
             + self.dp_row_std('population_25_years_and_older') \
             + self.dp_row_std('bachelors_degree_or_higher') \
             + self.dp_row_std('graduate_degree_or_higher') \
             + self.dp_full_row_str('INCOME') \
             + self.dp_row_nc('per_capita_income') \
             + self.dp_full_row_str('HOUSING') \
             + self.dp_row_nc('median_year_structure_built') \
             + self.dp_row_nc('median_value') \
             + self.dp_row_nc('median_rent') \
             + self.divider()

