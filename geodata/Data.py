from initialize_sqlalchemy import Base
from sqlalchemy import Column, Integer, String, Index, ForeignKey
from sqlalchemy.orm import relationship

def create_data_class(merged_df):
    # Dynamic table creation: Create an attr_dict to store table attributes
    attr_dict = {}

    # Set the name for the table.
    attr_dict['__tablename__'] = 'data'

    # Give the table an id column
    attr_dict['id'] = Column(Integer, primary_key=True)

    # Dynamically add the other columns
    for column in merged_df.columns:
        if column == 'LOGRECNO':
            attr_dict[column] = Column(String, 
                ForeignKey('place_counties.logrecno'))
        else:
            attr_dict[column] = Column(String)

    # Define the __repr__ for the new class
    def _repr(self):
        return "<Data(LOGRECNO='%s' ...)>" % (self.LOGRECNO)

    # Add the definition above to the class
    attr_dict['__repr__'] = _repr

    # Add the relationship
    attr_dict['placecounty'] = relationship('PlaceCounty',
        back_populates='data')

    # attr_dict
    return type('Data', (Base,), attr_dict)
