from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://@localhost:5432/residential_buildings')
Session = sessionmaker(bind=engine)

Base = declarative_base()


def get_session():
    return Session()
