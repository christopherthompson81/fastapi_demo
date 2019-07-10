'''
FastAPI Demo

User utils
'''
# Standard Imports

# PyPi Imports
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Local Imports
from database import models
from data_schemas import schemas

###############################################################################

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

###############################################################################

def get_user(database: Session, user_id: int):
	'''Get a specific user by user_id'''
	return database.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(database: Session, email: str):
	'''Get a specific user by email address'''
	return database.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(database: Session, username: str):
	'''Get a specific user by username'''
	return database.query(models.User).filter(models.User.username == username).first()

def get_users(database: Session, skip: int = 0, limit: int = 100):
	'''Get a list of users'''
	return database.query(models.User).offset(skip).limit(limit).all()

def hash_password(username: str, password: str):
	'''Salt and hash a password'''
	salted_password = password + username
	return PWD_CONTEXT.hash(salted_password)

def verify_password(username: str, plain_password: str, hashed_password: str):
	'''Verify a salted and hashed password against the username / password pair'''
	salted_password = plain_password + username
	return PWD_CONTEXT.verify(salted_password, hashed_password)

def authenticate_user(database: Session, username: str, password: str):
	'''Authenticate a user'''
	user = get_user_by_username(database, username)
	#salted_password = password + username
	#print(PWD_CONTEXT.hash(salted_password))
	if not user:
		return False
	if not verify_password(username, password, user.salted_password_hash):
		return False
	return user

def create_user(database: Session, user: schemas.UserCreate):
	'''Create a new user'''
	db_user = models.User(
		username=user.username,
		first_name=user.first_name,
		last_name=user.last_name,
		email=user.email,
		salted_password_hash=hash_password(user.username, user.password)
	)
	database.add(db_user)
	database.commit()
	database.refresh(db_user)
	return db_user

def update_user(database: Session, user_id: int, data: schemas.UserUpdate):
	'''Update a user'''
	user = get_user(database=database, user_id=user_id)
	if data.first_name:
		user.first_name = data.first_name
	if data.last_name:
		user.last_name = data.last_name
	if data.email:
		user.email = data.email
	database.add(user)
	database.commit()
	return user

def delete_user(database: Session, user_id: int):
	'''Delete a user'''
	user = get_user(database=database, user_id=user_id)
	database.delete(user)
	database.commit()
	return user

def set_password(database: Session, user_id: int, password: str):
	'''Change a password'''
	user = get_user(database=database, user_id=user_id)
	user.salted_password_hash = hash_password(username=user.username, password=password)
	database.add(user)
	database.commit()

def set_user_admin(database: Session, user_id: int, admin: bool):
	'''Set the admin flag on a user'''
	user = get_user(database=database, user_id=user_id)
	user.admin_boolean = admin
	database.add(user)
	database.commit()

def set_user_active(database: Session, user_id: int, active: bool):
	'''Set the admin flag on a user'''
	user = get_user(database=database, user_id=user_id)
	user.active_boolean = active
	database.add(user)
	database.commit()
