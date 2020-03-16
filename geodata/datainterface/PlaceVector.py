'''
A standard 8-dimensional vector used to compare places with others.

The closer one PlaceVector's euclidean distance is to another, the more
demographically similar two places representing them are.
'''

class PlaceVector:
    '''A standard 8-dimensional vector used to compare places with others.'''
    def __init__(
        self,
        db_row,
        medians,
        standard_deviations
        ):

        self.name = db_row['NAME']
        # self.county = county

        population = db_row['B01003_1']
        land_area_sqmi = db_row['ALAND_SQMI']
        per_capita_income = db_row['B19301_1']
        white_alone = db_row['B02001_2']
        black_alone = db_row['B02001_3']
        asian_alone = db_row['B02001_5']
        hispanic_or_latino = db_row['B03002_12']
        population_25_years_or_older = db_row['B15003_1']
        bachelors_degree = db_row['B15003_22']
        masters_degree = db_row['B15003_23']
        professional_school_degree = db_row['B15003_24']
        doctorate_degree = db_row['B15003_25']

        # Raw subcomponents - Raw values of each subcomponent
        self.rs = dict()

        if population != 0:
            self.rs['population_density'] = int(population) / float(land_area_sqmi)
            self.rs['per_capita_income'] = int(per_capita_income)
            self.rs['white_alone'] = float(white_alone) / float(population) * 100.0
            self.rs['black_alone'] = float(black_alone) / float(population) * 100.0
            self.rs['asian_alone'] = float(asian_alone) / float(population) * 100.0
            self.rs['hispanic_or_latino'] = float(hispanic_or_latino) / float(population) * 100.0
            if int(population_25_years_or_older) != 0:
                self.rs['bachelors_degree_or_higher'] = ( int(bachelors_degree) \
                    + int(masters_degree) + int(professional_school_degree) \
                    + int(doctorate_degree) ) / int(population_25_years_or_older)  * 100.0
                self.rs['graduate_degree_or_higher'] = ( int(masters_degree) \
                    + int(professional_school_degree) + int(doctorate_degree) ) \
                    / int(population_25_years_or_older)  * 100.0
            else:
                self.rs['bachelors_degree_or_higher'] = 0.0
                self.rs['graduate_degree_or_higher'] = 0.0

        else:
            self.rs['population_density'] = 0.0
            self.rs['per_capita_income'] = 0
            self.rs['white_alone'] = 0.0
            self.rs['black_alone'] = 0.0
            self.rs['asian_alone'] = 0.0
            self.rs['hispanic_or_latino'] = 0.0
            self.rs['bachelors_degree_or_higher'] = 0.0
            self.rs['graduate_degree_or_higher'] = 0.0

        # Get medians for each subcomponent
        self.med = dict()

        if population != 0:
            self.med['population_density'] = float(medians['B01003_1']) / float(medians['ALAND_SQMI'])
            self.med['per_capita_income'] = float(medians['B19301_1'])
            self.med['white_alone'] = float(medians['B02001_2']) / float(medians['B01003_1']) * 100.0
            self.med['black_alone'] = float(medians['B02001_3']) / float(medians['B01003_1']) * 100.0
            self.med['asian_alone'] = float(medians['B02001_5']) / float(medians['B01003_1']) * 100.0
            self.med['hispanic_or_latino'] = float(medians['B03002_12']) / float(medians['B01003_1']) * 100.0
            if int(population_25_years_or_older) != 0:
                self.med['bachelors_degree_or_higher'] = (int(medians['B15003_22']) + int(medians['B15003_23']) \
                + int(medians['B15003_24']) + int(medians['B15003_25'])) / float(medians['B15003_1']) * 100.0
                self.med['graduate_degree_or_higher'] = (int(medians['B15003_23']) \
                + int(medians['B15003_24']) + int(medians['B15003_25'])) / float(medians['B15003_1']) * 100.0
            else:
                self.med['bachelors_degree_or_higher'] = 0.0
                self.med['graduate_degree_or_higher'] = 0.0
        else:
            self.med['population_density'] = 0.0
            self.med['per_capita_income'] = 0
            self.med['white_alone'] = 0.0
            self.med['black_alone'] = 0.0
            self.med['asian_alone'] = 0.0
            self.med['hispanic_or_latino'] = 0.0
            self.med['bachelors_degree_or_higher'] = 0.0
            self.med['graduate_degree_or_higher'] = 0.0


        # Get standard deviations for each subcomponent
        self.sd = dict()

        if population != 0:
            self.sd['population_density'] = float(standard_deviations['B01003_1']) / float(standard_deviations['ALAND_SQMI'])
            self.sd['per_capita_income'] = float(standard_deviations['B19301_1'])
            self.sd['white_alone'] = float(standard_deviations['B02001_2']) / float(standard_deviations['B01003_1']) * 100.0
            self.sd['black_alone'] = float(standard_deviations['B02001_3']) / float(standard_deviations['B01003_1']) * 100.0
            self.sd['asian_alone'] = float(standard_deviations['B02001_5']) / float(standard_deviations['B01003_1']) * 100.0
            self.sd['hispanic_or_latino'] = float(standard_deviations['B03002_12']) / float(standard_deviations['B01003_1']) * 100.0
            if int(population_25_years_or_older) != 0:
                self.sd['bachelors_degree_or_higher'] = (int(standard_deviations['B15003_22']) + int(standard_deviations['B15003_23']) \
                + int(standard_deviations['B15003_24']) + int(standard_deviations['B15003_25'])) / float(standard_deviations['B15003_1']) * 100.0
                self.sd['graduate_degree_or_higher'] = (int(standard_deviations['B15003_23']) \
                + int(standard_deviations['B15003_24']) + int(standard_deviations['B15003_25'])) / float(standard_deviations['B15003_1']) * 100.0
            else:
                self.sd['bachelors_degree_or_higher'] = 0.0
                self.sd['graduate_degree_or_higher'] = 0.0
        else:
            self.sd['population_density'] = 0.0
            self.sd['per_capita_income'] = 0
            self.sd['white_alone'] = 0.0
            self.sd['black_alone'] = 0.0
            self.sd['asian_alone'] = 0.0
            self.sd['hispanic_or_latino'] = 0.0
            self.sd['bachelors_degree_or_higher'] = 0.0
            self.sd['graduate_degree_or_higher'] = 0.0

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
        # The race component:
        #   White alone (25%)
        #   Black alone (25%)
        #   Asian alone (25%)
        #   Hispanic or Latino (25%)*
        #
        # * Note: Hispanic or Latino is not a race as far as the Census is
        # concerned. To the Census, a person is either Hispanic or Latino or they
        # are not, and in addition to that they are of some race. But for
        # PlaceVector calculation purposes, that category makes up 25% of the race
        # component.
        #

        self.ws['white_alone'] = self.s['white_alone'] / 4
        self.ws['black_alone'] = self.s['black_alone'] / 4
        self.ws['asian_alone'] = self.s['asian_alone'] / 4
        self.ws['hispanic_or_latino'] = self.s['hispanic_or_latino'] / 4

        #
        # The education component:
        #   Bachelor's degree or higher (50%)
        #   Graduate degree or higher (50%)
        #

        self.ws['bachelors_degree_or_higher'] = self.s['bachelors_degree_or_higher'] / 2
        self.ws['graduate_degree_or_higher'] = self.s['graduate_degree_or_higher'] / 2

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
        return 'PlaceVector(' + self.name + '\ns:' \
            + ', '.join([str((i,j)) for i,j in self.s.items()]) + ')'
