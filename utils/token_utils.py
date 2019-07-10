'''
FastAPI Demo

CRUD utils
'''
# Standard Imports
from datetime import datetime, timedelta

# PyPi Imports
import jwt

# Local Imports
from utils.config_utils import get_config

###############################################################################

CONFIG = get_config('security.cfg')
SECURITY = CONFIG['security']

###############################################################################

def create_access_token(*, data: dict, expires_delta: timedelta = None):
	'''Create a JWT token with the provided data'''
	to_encode = data.copy()
	expire = datetime.utcnow() + expires_delta if expires_delta else timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECURITY['SECRET_KEY'], algorithm=SECURITY['ALGORITHM'])
	return encoded_jwt
