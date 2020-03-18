import csv

class CSVTools:
    '''
    Tools to deal with CSV files.
    '''
    def __init__(self, path):
        states = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'dc', 'de',
        'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md',
        'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny',
        'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut',
        'vt', 'va', 'wa', 'wv', 'wi', 'wy']

        # Get rows from CSV files for each state.
        self.rows = []

        for state in states:
            this_path = path + 'g20185' + state + '.csv'
            with open(this_path, 'rt', encoding='iso-8859-1') as f:
                self.rows += list(csv.reader(f))

        # Get rows from the US CSV file.
        # Note: This file doesn't contain places. It's only useful for states
        # and ZCTAs.
        self.us_rows = []

        this_path = path + 'g20185us.csv'
        with open(this_path, 'rt', encoding='iso-8859-1') as f:
            self.us_rows += list(csv.reader(f))
