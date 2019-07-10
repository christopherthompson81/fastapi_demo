'''
FastAPI Demo

/token router
'''
# Standard Imports
from datetime import timedelta

# PyPi Imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.status import (
	HTTP_400_BAD_REQUEST,
	HTTP_401_UNAUTHORIZED
)

# Local Imports
from utils.config_utils import get_config
from utils.main_utils import get_db
from utils.token_utils import create_access_token
from utils.user_utils import (
	authenticate_user,
	get_user
)
from data_schemas import schemas

###############################################################################

CONFIG = get_config('security.cfg')
SECURITY = CONFIG['security']

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") #pylint: disable=invalid-name

router = APIRouter() #pylint: disable=invalid-name

###############################################################################

AUTHENTICATION_EXCEPTION = HTTPException(
	status_code=HTTP_401_UNAUTHORIZED,
	detail="Incorrect username or password",
	headers={"WWW-Authenticate": "Bearer"},
)

CREDENTIALS_EXCEPTION = HTTPException(
	status_code=HTTP_401_UNAUTHORIZED,
	detail="Could not validate credentials",
	headers={"WWW-Authenticate": "Bearer"}
)

INACTIVE_USER_EXCEPTION = HTTPException(
	status_code=HTTP_401_UNAUTHORIZED,
	detail="Inactive user"
)

TOKEN_PROCESSING_EXCEPTION = HTTPException(
	status_code=HTTP_400_BAD_REQUEST,
	detail="JWT could not be processed",
	headers={"WWW-Authenticate": "Bearer"}
)

TOKEN_EXPIRED_EXCEPTION = HTTPException(
	status_code=HTTP_401_UNAUTHORIZED,
	detail="Token Expired. Reauthenticate",
	headers={"WWW-Authenticate": "Bearer"}
)

###############################################################################

async def get_token(token: str = Depends(oauth2_scheme)):
	#payload: str = Depends(oauth2_scheme),
	'''Make sure the supplied token is one of ours'''
	try:
		payload = jwt.decode(token, SECURITY['SECRET_KEY'], algorithms=[SECURITY['ALGORITHM']])
	except jwt.ExpiredSignatureError:
		raise TOKEN_EXPIRED_EXCEPTION
	except jwt.PyJWTError:
		raise TOKEN_PROCESSING_EXCEPTION
	return payload

async def check_token(payload: dict = Depends(get_token)):
	#payload: str = Depends(oauth2_scheme),
	'''Make sure the supplied token is satisfactory'''
	return bool(payload)

async def check_current_user(
	request: Request,
	payload: dict = Depends(get_token),
	database: Session = Depends(get_db)
):
	'''Get the current user based on the included token'''
	user_id: str = payload.get("user_id")
	if user_id is None:
		raise CREDENTIALS_EXCEPTION
	user = get_user(database=database, user_id=user_id)
	if user is None:
		raise CREDENTIALS_EXCEPTION
	if not user.active_boolean:
		raise INACTIVE_USER_EXCEPTION
	request.state.current_user = user
	return user

###############################################################################

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
	form_data: OAuth2PasswordRequestForm = Depends(),
	database: Session = Depends(get_db)
):
	'''Issue a token if the credentials authenticate'''
	user = authenticate_user(database=database, username=form_data.username, password=form_data.password)
	if not user:
		raise AUTHENTICATION_EXCEPTION
	if not user.active_boolean:
		raise INACTIVE_USER_EXCEPTION
	access_token_expires = timedelta(minutes=int(SECURITY['ACCESS_TOKEN_EXPIRE_MINUTES']))
	access_token = create_access_token(data={"user_id": user.user_id}, expires_delta=access_token_expires)
	return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token/refresh", response_model=schemas.Token)
async def refresh_expired_access_token(
	token: str = Depends(oauth2_scheme),
	database: Session = Depends(get_db)
):
	'''Issue a replacement token if the current access token is not expired, or only recently expired.'''
	try:
		payload = jwt.decode(
			token,
			SECURITY['SECRET_KEY'],
			algorithms=[SECURITY['ALGORITHM']],
			leeway=int(SECURITY['REFRESH_TOKEN_LEEWAY_SECONDS'])
		)
	except jwt.ExpiredSignatureError:
		raise TOKEN_EXPIRED_EXCEPTION
	except jwt.PyJWTError:
		raise TOKEN_PROCESSING_EXCEPTION
	user_id: str = payload.get("user_id")
	if user_id is None:
		raise CREDENTIALS_EXCEPTION
	user = get_user(database=database, user_id=user_id)
	if not user:
		raise AUTHENTICATION_EXCEPTION
	if not user.active_boolean:
		raise INACTIVE_USER_EXCEPTION
	access_token_expires = timedelta(minutes=int(SECURITY['ACCESS_TOKEN_EXPIRE_MINUTES']))
	access_token = create_access_token(data={"user_id": user.user_id}, expires_delta=access_token_expires)
	return {"access_token": access_token, "token_type": "bearer"}
