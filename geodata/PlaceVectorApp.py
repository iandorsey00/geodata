#
# PlaceVectorApp.py
#
# A 3-dimensional vector that represents a place's appearance.
#
# The closer one PlaceVector's euclidean distance is to another, the more
# similar two places representing them are.
#

class PlaceVectorApp:
    '''A standard 8-dimensional vector used to compare places with others.'''
    def __init__(
        self,
        name,
        county,
        population,
        per_capita_income,
        land_area_sqmi,
        median_year_structure_built,
        medians,
        standard_deviations
        ):

        self.name = name
        self.county = county

        # Raw subcomponents - Raw values of each subcomponent
        self.rs = dict()

        # Population density
        self.rs['population_density']  = int(population) / float(land_area_sqmi)
        self.rs['per_capita_income'] = int(per_capita_income)
        self.rs['median_year_structure_built'] = int(median_year_structure_built)

        # Get medians for each subcomponent
        self.med = dict()

        self.med['population_density'] = float(medians[0]) / float(medians[5])
        self.med['per_capita_income'] = float(medians[1])
        self.med['median_year_structure_built'] = float(medians[6])

        # Get standard deviations for each subcomponent
        self.sd = dict()

        self.sd['population_density'] = float(standard_deviations[0]) / float(standard_deviations[5])
        self.sd['per_capita_income'] = float(standard_deviations[1])
        self.sd['median_year_structure_built'] = float(standard_deviations[6])

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
        # two standard deviations from the median, the score is the ratio of
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
            elif self.rs[sc] > self.med[sc] and self.rs[sc] < self.med[sc] + (self.sd[sc] * 2):
                self.s[sc] = \
                int(
                    round( 
                            50 + (
                            (self.rs[sc] - self.med[sc]) / (self.sd[sc] * 2)
                            ) * 50
                    )
                )
            else: # self.rs[sc] > self.med[sc] + (self.sd[sc] * 2)
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

    # Calculate the euclidean distance between place vectors.
    def distance(self, other):
        distance = 0

        # Square the difference of each subcomponent, then add them together.
        for sc in self.ws.keys():
            distance += (self.ws[sc] - other.ws[sc]) ** 2

        import math

        # Return the square root of that sum.
        return math.sqrt(distance)

    # Display subcomponent scores
    def __repr__(self):
        return 'PlaceVectorApp(' + self.name + ': ' + self.county + '\ns:' \
            + ', '.join([str((i,j)) for i,j in self.s.items()]) + ')'
