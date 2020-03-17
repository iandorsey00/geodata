'''
This file ensures all other files use the same SQLAlchemy session and Base.

Other files should import engine, session, and Base when needed. Use:

    from initialize_sqlalchemy import Base, session, engine
'''

# The engine
from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')

# The session
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# The Base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
