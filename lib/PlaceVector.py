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
        land_area_sqmi
        ):

        # Raw subcomponents - Raw values of each subcomponent
        self.rs = dict()

        # Population density
        self.rs['population']  = int(population) / float(land_area_sqmi)
        self.rs['income']      = int(per_capita_income)
        self.rs['white_alone'] = float(white_alone) / float(population) * 100.0
        self.rs['black_alone'] = float(black_alone) / float(population) * 100.0
        self.rs['asian_alone'] = float(asian_alone) / float(population) * 100.0
        self.rs['hispanic_or_latino_alone'] = float(hispanic_or_latino_alone) / float(population) * 100.0
        self.rs['bachelors_degree_or_higher'] = ( int(bachelors_degree) \
            + int(masters_degree) + int(professional_school_degree) \
            + int(doctorate_degree) ) / int(population_25_years_or_older)
        self.rs['graduate_degree_or_higher'] = ( int(masters_degree) \
            + int(professional_school_degree) + int(doctorate_degree) ) \
            / int(population_25_years_or_older)
    
    # For now, just display the raw subcomponents.
    def __repr__(self):
        return 'PlaceVector(rs:' + ', '.join([str((i,j)) for i,j in self.rs.items()]) + ')'
