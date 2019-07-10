'''
FastAPI Demo

SQLAlchemy ORM Models
'''
# Standard Imports

# PyPi Imports
from sqlalchemy import (
	Boolean,
	Column,
	Integer,
	String
)

# Local Imports
from database.setup import Base

###############################################################################

class User(Base):
	'''ORM Models - users'''
	__tablename__ = "users"
	user_id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True)
	salted_password_hash = Column(String)
	first_name = Column(String)
	last_name = Column(String)
	email = Column(String, unique=True)
	active_boolean = Column(Boolean, nullable=False, default=True)
	admin_boolean = Column(Boolean, nullable=False, default=False)
