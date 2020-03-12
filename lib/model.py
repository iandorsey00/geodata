#
# model.py
#
# Provides insert_rows, a function to insert rows using a model.
#

import pandas as pd
from initialize_sqlalchemy import Base, engine, session

def insert_rows(model, read_csv_file, cols=None, dtype='str',
                header='infer', sep=','):
        # Create all tables so far.
        Base.metadata.create_all(engine)

        # Place data into DataFrame
        # e.g. df = pd.read_csv('../data/ACS_5yr_Seq_Table_Number_Lookup.txt',
        #           dtype='str')
        df = pd.read_csv(read_csv_file, dtype=dtype, header=header, sep=sep)

        if cols is None:
            columns = df.columns
        else:
            columns = cols

        # Declare a list to store column headers
        data_rows = []

        for index, data in df.iterrows():
            # Create column header models
            model_instance = model()

            for idx, column in enumerate(columns):
                # Dynamically assign data to each attribute
                setattr(model_instance, column, data[idx])
            
            data_rows.append(model_instance)

        # Add column headers to database
        session.add_all(data_rows)
