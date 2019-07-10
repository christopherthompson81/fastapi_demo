'''
FastAPI Demo

Database setup
'''
# Standard Imports

# PyPi Imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Local Imports
from utils.config_utils import get_config

###############################################################################
CONFIG = get_config('database.cfg')
DB_CONFIG = CONFIG['database']
DB_URL_MASK = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'
DB_URL = DB_URL_MASK.format(
    user=DB_CONFIG['POSTGRES_USER'],
    pw=DB_CONFIG['POSTGRES_PW'],
    url=DB_CONFIG['POSTGRES_URL'],
    db=DB_CONFIG['POSTGRES_DB']
)
SQLALCHEMY_DATABASE_URL = DB_URL

###############################################################################

engine = create_engine(SQLALCHEMY_DATABASE_URL) #pylint: disable=invalid-name

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine) #pylint: disable=invalid-name

Base = declarative_base() #pylint: disable=invalid-name
