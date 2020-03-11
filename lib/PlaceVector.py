#
# PlaceVector.py
#
# A standard 8-dimensional vector used to compare places with others.
#
# The closer one PlaceVector's euclidean distance is to another, the more
# similar two places representing them are.
#

class PlaceVector:
    '''A standard 8-dimensional vector used to compare places with others.'''
    def __init__(
        self,
        name,
        county,
        population,
        per_capita_income,
        white_alone,
        black_alone,
        asian_alone,
        hispanic_or_latino_alone,
        population_25_years_or_older,
        bachelors_degree,
        masters_degree,
        professional_school_degree,
        doctorate_degree,
        land_area_sqmi,
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
        self.rs['white_alone'] = float(white_alone) / float(population) * 100.0
        self.rs['black_alone'] = float(black_alone) / float(population) * 100.0
        self.rs['asian_alone'] = float(asian_alone) / float(population) * 100.0
        self.rs['hispanic_or_latino_alone'] = float(hispanic_or_latino_alone) / float(population) * 100.0
        self.rs['bachelors_degree_or_higher'] = ( int(bachelors_degree) \
            + int(masters_degree) + int(professional_school_degree) \
            + int(doctorate_degree) ) / int(population_25_years_or_older)  * 100.0
        self.rs['graduate_degree_or_higher'] = ( int(masters_degree) \
            + int(professional_school_degree) + int(doctorate_degree) ) \
            / int(population_25_years_or_older)  * 100.0

        # Get medians for each subcomponent
        self.med = dict()

        self.med['population_density'] = float(medians[0]) / float(medians[11])
        self.med['per_capita_income'] = float(medians[1])
        self.med['white_alone'] = float(medians[2]) / float(medians[0]) * 100.0
        self.med['black_alone'] = float(medians[3]) / float(medians[0]) * 100.0
        self.med['asian_alone'] = float(medians[4]) / float(medians[0]) * 100.0
        self.med['hispanic_or_latino_alone'] = float(medians[5]) / float(medians[0]) * 100.0
        self.med['bachelors_degree_or_higher'] = (int(medians[7]) + int(medians[8]) \
        + int(medians[9]) + int(medians[10])) / float(medians[6]) * 100.0
        self.med['graduate_degree_or_higher'] = (int(medians[8]) \
        + int(medians[9]) + int(medians[10])) / float(medians[6]) * 100.0

        # Get standard deviations for each subcomponent
        self.sd = dict()

        self.sd['population_density'] = float(standard_deviations[0]) / float(standard_deviations[11])
        self.sd['per_capita_income'] = float(standard_deviations[1])
        self.sd['white_alone'] = float(standard_deviations[2]) / float(standard_deviations[0]) * 100.0
        self.sd['black_alone'] = float(standard_deviations[3]) / float(standard_deviations[0]) * 100.0
        self.sd['asian_alone'] = float(standard_deviations[4]) / float(standard_deviations[0]) * 100.0
        self.sd['hispanic_or_latino_alone'] = float(standard_deviations[5]) / float(standard_deviations[0]) * 100.0
        self.sd['bachelors_degree_or_higher'] = (int(standard_deviations[7]) + int(standard_deviations[8]) \
        + int(standard_deviations[9]) + int(standard_deviations[10])) / float(standard_deviations[6]) * 100.0
        self.sd['graduate_degree_or_higher'] = (int(standard_deviations[8]) \
        + int(standard_deviations[9]) + int(standard_deviations[10])) / float(standard_deviations[6]) * 100.0

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

    # Display subcomponent scores
    def __repr__(self):
        return 'PlaceVector(' + self.name + ': ' + self.county + '; s:' \
            + ', '.join([str((i,j)) for i,j in self.s.items()]) + ')'
