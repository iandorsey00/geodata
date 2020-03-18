class StateTools:
    '''Tools to convert state names to abbreviations, etc.'''
    def get_state(self, geo_name):
        '''Get the state name given a Census display label.'''
        # Split the name string by ', '
        if ';' in geo_name:
            split_geo_name = geo_name.split('; ')
        else:
            split_geo_name = geo_name.split(', ')
        return split_geo_name[-1]

    def get_abbrevs(self, lowercase=False):
        '''Get two-letter state abbreviations.'''
        if not lowercase:
            return self.abbrevs
        else:
            return list(map(lambda x: x.lower(), self.abbrevs))

    def get_abbrev(self, name, lowercase=False):
        '''Transform a state name into its abbreviation.'''
        if not lowercase:
            return self.name_to_abbrev[name]
        else:
            return self.name_to_abbrev[name].lower()

    def get_name(self, abbrev):
        '''Transform a state abbreviation into its name.'''
        return self.state_abbrev_to_name[abbrev.upper()]

    def __init__(self, csvt_instance):
        # Rows from CSV files
        rows = csvt_instance.rows
                
        # Filter for summary level code 040 (State-Places)
        these_rows = list(filter(lambda x: x[2] == '040', rows))
        
        # geoid_to_name #######################################################
        # name_to_geoid #######################################################
        self.geoid_to_name = dict()
        self.name_to_geoid = dict()

        for row in these_rows:
            geoid = row[48][7:]
            name = row[49]

            self.geoid_to_name[geoid] = name
            self.name_to_geoid[name] = geoid

        # Begin long lists ####################################################
        self.abbrevs = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE',
        'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
        'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
        'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

        self.name_to_abbrev = {
            'Alaska': 'AK',
            'Alabama': 'AL',
            'Arkansas': 'AR',
            'American Samoa': 'AS',
            'Arizona': 'AZ',
            'California': 'CA',
            'Colorado': 'CO',
            'Connecticut': 'CT',
            'District of Columbia': 'DC',
            'Delaware': 'DE',
            'Florida': 'FL',
            'Georgia': 'GA',
            'Guam': 'GU',
            'Hawaii': 'HI',
            'Iowa': 'IA',
            'Idaho': 'ID',
            'Illinois': 'IL',
            'Indiana': 'IN',
            'Kansas': 'KS',
            'Kentucky': 'KY',
            'Louisiana': 'LA',
            'Massachusetts': 'MA',
            'Maryland': 'MD',
            'Maine': 'ME',
            'Michigan': 'MI',
            'Minnesota': 'MN',
            'Missouri': 'MO',
            'Northern Mariana Islands': 'MP',
            'Mississippi': 'MS',
            'Montana': 'MT',
            'National': 'NA',
            'North Carolina': 'NC',
            'North Dakota': 'ND',
            'Nebraska': 'NE',
            'New Hampshire': 'NH',
            'New Jersey': 'NJ',
            'New Mexico': 'NM',
            'Nevada': 'NV',
            'New York': 'NY',
            'Ohio': 'OH',
            'Oklahoma': 'OK',
            'Oregon': 'OR',
            'Pennsylvania': 'PA',
            'Puerto Rico': 'PR',
            'Rhode Island': 'RI',
            'South Carolina': 'SC',
            'South Dakota': 'SD',
            'Tennessee': 'TN',
            'Texas': 'TX',
            'Utah': 'UT',
            'Virginia': 'VA',
            'Virgin Islands': 'VI',
            'Vermont': 'VT',
            'Washington': 'WA',
            'Wisconsin': 'WI',
            'West Virginia': 'WV',
            'Wyoming': 'WY'
        }

        self.state_abbrev_to_name = dict()

        for name, abbrev in self.name_to_abbrev.items():
            self.state_abbrev_to_name[abbrev] = name
