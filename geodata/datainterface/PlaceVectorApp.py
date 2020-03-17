#
# PlaceVectorApp.py
#
# A 3-dimensional vector that represents a place's appearance.
#
# The closer one PlaceVector's euclidean distance is to another, the more
# similar two places representing them are.
#

class PlaceVectorApp:
    '''A 3-dimensional vector used to compare place appearances.'''
    def __init__(
        self,
        db_row,
        medians,
        standard_deviations
        ):

        self.name = db_row['NAME']
        self.state = db_row['STATE_ABBREV']
        # self.county = county

        population = db_row['B01003_1']
        self.population = int(population)
        land_area_sqmi = db_row['ALAND_SQMI']
        per_capita_income = db_row['B19301_1']
        median_year_structure_built = db_row['B25035_1']

        # Raw subcomponents - Raw values of each subcomponent
        self.rs = dict()

        # Population density
        self.rs['population_density']  = int(population) / float(land_area_sqmi)
        self.rs['per_capita_income'] = int(per_capita_income)
        # Subtract 1939 because the U.S. Census Bureau doesn't record year
        # structure built values that are earlier than 1939. (1939=0)
        self.rs['median_year_structure_built'] = int(median_year_structure_built) - 1939

        # Get medians for each subcomponent
        self.med = dict()

        self.med['population_density'] = float(medians['B01003_1']) / float(medians['ALAND_SQMI'])
        self.med['per_capita_income'] = float(medians['B19301_1'])
        # Subtract 1939 because the U.S. Census Bureau doesn't record year
        # structure built values that are earlier than 1939. (1939=0)
        self.med['median_year_structure_built'] = float(medians['B25035_1']) - 1939

        # Get standard deviations for each subcomponent
        self.sd = dict()

        self.sd['population_density'] = float(standard_deviations['B01003_1']) / float(standard_deviations['ALAND_SQMI'])
        self.sd['per_capita_income'] = float(standard_deviations['B19301_1'])
        self.sd['median_year_structure_built'] = float(standard_deviations['B25035_1'])

        #######################################################################
        # Calculate subcomponent scores
        #
        # Scores for each subcomponent are calculated as follows.
        #
        # If the value for the subcomponent is below the median, then
        # score is the ratio of the value and the median times 50. (In simple
        # terms, we are assigning a proportional value between 0 and 50.)
        #
        # If the value for the subcomponent is at the median, the score is 50.
        #
        # If the value for the subcomponent is above the median but below
        # three standard deviations from the median, the score is the ratio of
        # the value and (the median plus two standard deviations) times 100.
        # (In simple terms, we are assigning a proportional value between 50
        # and 100.)
        #
        # If the value for the subcomponent is at the median plus two standard
        # deviations or more, the score will be 100.

        # Create a dictionary to store subcomponents
        self.s = dict()

        # sc = s = subcomponent
        # rs = raw subcomponent
        # med = median
        # sd = standard deviation
        for sc in self.rs.keys():
            if self.rs[sc] < self.med[sc]:
                self.s[sc] = \
                int(
                    round( (self.rs[sc] / self.med[sc]) * 50 )
                )
            elif self.rs[sc] == self.med[sc]:
                self.s[sc] = 50
            elif self.rs[sc] > self.med[sc] and self.rs[sc] < self.med[sc] + (self.sd[sc] * 3):
                self.s[sc] = \
                int(
                    round( 
                            50 + (
                            (self.rs[sc] - self.med[sc]) / (self.sd[sc] * 3)
                            ) * 50
                    )
                )
            else: # self.rs[sc] > self.med[sc] + (self.sd[sc] * 3)
                self.s[sc] = 100

        #######################################################################
        # Weighted subcomponents
        #
        # Though the __repr__ for PlaceVector will only display unweighted
        # subcomponents, the weight subcomponents will be the ones actually
        # involved in the distance calculation between PlaceVectors.
        #
        # Groups of weighted subcomponents make up each component shown below.

        self.ws = dict()

        #
        # The population density component:
        #   Population density (100%)
        #

        self.ws['population_density'] = self.s['population_density']

        #
        # The income component:
        #   Per capita income (100%)
        #

        self.ws['per_capita_income'] = self.s['per_capita_income']

        #
        # The median year structure built component:
        #   Median year structure built (100%)
        #

        self.ws['median_year_structure_built'] = self.s['median_year_structure_built']

    def distance(self, other):
        '''Calculate the euclidean distance between place vectors.'''
        distance = 0

        # Square the difference of each subcomponent, then add them together.
        for sc in self.ws.keys():
            distance += (self.ws[sc] - other.ws[sc]) ** 2

        import math

        # Return the square root of that sum.
        return math.sqrt(distance)

    def __repr__(self):
        '''Display subcomponent scores.'''
        return 'PlaceVectorApp(' + self.name + ', population: ' + f'{self.population:,}' + '\ns:' \
            + ', '.join([str((i,j)) for i,j in self.s.items()]) + ')'
