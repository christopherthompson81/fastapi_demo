'''
FastAPI Demo

/users router
'''
# Standard Imports
from typing import List

# PyPi Imports
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette.status import (
	HTTP_403_FORBIDDEN,
	HTTP_409_CONFLICT,
	HTTP_422_UNPROCESSABLE_ENTITY
)

# Local Imports
from data_schemas import schemas
from database import models
from utils.config_utils import get_config
from utils.main_utils import (
	get_current_user,
	get_db
)
import utils.user_utils as user_utils

###############################################################################

CONFIG = get_config('security.cfg')
SECURITY = CONFIG['security']

router = APIRouter() #pylint: disable=invalid-name

###############################################################################

PRIVILEGE_EXCEPTION = HTTPException(
	status_code=HTTP_403_FORBIDDEN,
	detail="Authenticated user lacks administrative privileges"
)

SELF_PRIVILEGE_EXCEPTION = HTTPException(
	status_code=HTTP_403_FORBIDDEN,
	detail="You may not change your own administrative privileges or active status"
)

USERNAME_CONFLICT_EXCEPTION = HTTPException(
	status_code=HTTP_409_CONFLICT,
	detail="Username already registered"
)

NO_USER_EXCEPTION = HTTPException(
	status_code=HTTP_422_UNPROCESSABLE_ENTITY,
	detail="No such user_id"
)

###############################################################################

@router.post("/users/", response_model=schemas.User)
def create_user(
	user: schemas.UserCreate,
	database: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user)
):
	'''Create a new user'''
	if not current_user.admin_boolean:
		raise PRIVILEGE_EXCEPTION
	db_user = user_utils.get_user_by_username(database=database, username=user.username)
	if db_user:
		raise USERNAME_CONFLICT_EXCEPTION
	return user_utils.create_user(database=database, user=user)

@router.get("/users/", response_model=List[schemas.User])
def read_users(
	skip: int = 0,
	limit: int = 100,
	database: Session = Depends(get_db)
):
	'''Get a list of users'''
	users = user_utils.get_users(database=database, skip=skip, limit=limit)
	return users

#item_id: int = Path(..., title="The ID of the item to get"),
@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
	user_id: int = Path(..., title="The ID of the user to get"),
	database: Session = Depends(get_db)
):
	'''Get a list of users'''
	user = user_utils.get_user(database=database, user_id=user_id)
	if not user:
		raise NO_USER_EXCEPTION
	return user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
	user_data: schemas.UserUpdate,
	database: Session = Depends(get_db),
	user_id: int = Path(..., title="The ID of the user to update"),
	current_user: models.User = Depends(get_current_user)
):
	"""Updates a user"""
	if not current_user.admin_boolean:
		raise PRIVILEGE_EXCEPTION
	if not user_utils.get_user(database=database, user_id=user_id):
		raise NO_USER_EXCEPTION
	db_user = user_utils.update_user(database=database, user_id=user_id, data=user_data)
	return db_user

@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(
	database: Session = Depends(get_db),
	user_id: int = Path(..., title="The ID of the user to update"),
	current_user: models.User = Depends(get_current_user)
):
	"""Deletes a user"""
	if current_user.user_id != user_id and not current_user.admin_boolean:
		raise PRIVILEGE_EXCEPTION
	if not user_utils.get_user(database=database, user_id=user_id):
		raise NO_USER_EXCEPTION
	result = user_utils.delete_user(database=database, user_id=user_id)
	return result

@router.put("/users/{user_id}/set_password")
def change_user_password(
	password: str,
	user_id: int = Path(..., title="The ID of the user to update"),
	database: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user)
):
	"""Sets a password"""
	if current_user.user_id != user_id and not current_user.admin_boolean:
		raise PRIVILEGE_EXCEPTION
	if not user_utils.get_user(database=database, user_id=user_id):
		raise NO_USER_EXCEPTION
	user_utils.set_password(database=database, user_id=user_id, password=password)
	return {'message': 'Password successfully changed'}

@router.put("/users/{user_id}/set_admin")
def change_user_admin(
	admin: bool,
	user_id: int = Path(..., title="The ID of the user to update"),
	database: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user)
):
	"""Set the admin flag on a user"""
	if not current_user.admin_boolean:
		raise PRIVILEGE_EXCEPTION
	if current_user.user_id == user_id:
		raise SELF_PRIVILEGE_EXCEPTION
	if not user_utils.get_user(database=database, user_id=user_id):
		raise NO_USER_EXCEPTION
	user_utils.set_user_admin(database=database, user_id=user_id, admin=admin)
	return {'message': 'Admin flag successfully changed'}

@router.put("/users/{user_id}/set_active")
def change_user_active(
	active: bool,
	user_id: int = Path(..., title="The ID of the user to update"),
	database: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user)
):
	"""Set the admin flag on a user"""
	if not current_user.admin_boolean:
		raise PRIVILEGE_EXCEPTION
	if current_user.user_id == user_id:
		raise SELF_PRIVILEGE_EXCEPTION
	if not user_utils.get_user(database=database, user_id=user_id):
		raise NO_USER_EXCEPTION
	user_utils.set_user_active(database=database, user_id=user_id, active=active)
	return {'message': 'Active flag successfully changed'}
