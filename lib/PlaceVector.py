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

        # Raw subcomponents - Raw values of each subcomponent
        self.rs = dict()

        # Population density
        self.rs['population']  = int(population) / float(land_area_sqmi)
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

        self.med['population'] = float(medians[0])
        self.med['per_capita_income'] = float(medians[1])
        self.med['white_alone'] = float(medians[2]) / self.med['population'] * 100.0
        self.med['black_alone'] = float(medians[3]) / self.med['population'] * 100.0
        self.med['asian_alone'] = float(medians[4]) / self.med['population'] * 100.0
        self.med['hispanic_or_latino_alone'] = float(medians[5]) / self.med['population'] * 100.0
        self.med['bachelors_degree_or_higher'] = (int(medians[7]) + int(medians[8]) \
        + int(medians[9]) + int(medians[10]) + int(medians[11])) / float(medians[6]) * 100.0
        self.med['graduate_degree_or_higher'] = (int(medians[8]) \
        + int(medians[9]) + int(medians[10]) + int(medians[11])) / float(medians[6]) * 100.0

        # Get standard deviations for each subcomponent
        self.sd = dict()

        self.sd['population'] = float(standard_deviations[0])
        self.sd['per_capita_income'] = float(standard_deviations[1])
        self.sd['white_alone'] = float(standard_deviations[2]) / self.sd['population'] * 100.0
        self.sd['black_alone'] = float(standard_deviations[3]) / self.sd['population'] * 100.0
        self.sd['asian_alone'] = float(standard_deviations[4]) / self.sd['population'] * 100.0
        self.sd['hispanic_or_latino_alone'] = float(standard_deviations[5]) / self.sd['population'] * 100.0
        self.sd['bachelors_degree_or_higher'] = (int(standard_deviations[7]) + int(standard_deviations[8]) \
        + int(standard_deviations[9]) + int(standard_deviations[10]) + int(standard_deviations[11])) / float(standard_deviations[6]) * 100.0
        self.sd['graduate_degree_or_higher'] = (int(standard_deviations[8]) \
        + int(standard_deviations[9]) + int(standard_deviations[10]) + int(standard_deviations[11])) / float(standard_deviations[6]) * 100.0

        #######################################################################
        # Calculate subcomponents
    
    # For now, just display the raw subcomponents, medians, and standard deviations.
    def __repr__(self):
        return 'PlaceVector(rs:' + ', '.join([str((i,j)) for i,j in self.rs.items()]) + ')\n' \
        + 'Medians: ' + ', '.join([str((i,j)) for i,j in self.med.items()]) + '\n' \
        + 'Standard deviations: ' + ', '.join([str((i,j)) for i,j in self.sd.items()])
