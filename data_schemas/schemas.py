'''
FastAPI Demo

REST pydantic Models (not SQLAlchemy ORM Models)
'''
# Standard Imports

# PyPi Imports
from validate_email import validate_email
from pydantic import (
	BaseModel,
	validator
)

###############################################################################

class Token(BaseModel):
	'''Schema of a JWT authentication token'''
	access_token: str
	token_type: str


class UserBase(BaseModel):
	'''The base type of the user schema'''
	username: str
	first_name: str
	last_name: str
	email: str

	@validator('email')
	def validate_email(cls, p_email):
		'''Check that the supplied email address is a valid email address'''
		if not validate_email(p_email):
			raise ValueError('Not a valid email address')
		return p_email


class UserCreate(UserBase):
	'''User augmented with sensitive parameters'''
	password: str


class User(UserBase):
	'''User Schema'''
	user_id: int
	active_boolean: bool
	admin_boolean: bool

	class Config:
		'''Enable ORM Mode'''
		orm_mode = True


class UserUpdate(BaseModel):
	'''Schema for updating a user'''
	first_name: str = None
	last_name: str = None
	email: str = None

	@validator('email')
	def validate_email(cls, p_email):
		'''Check that the supplied email address is a valid email address'''
		if not validate_email(p_email):
			raise ValueError('Not a valid email address')
		return p_email
