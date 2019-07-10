'''
FastAPI Demo

Create the initial user
'''
from database.setup import session_local, engine
from database import models
from data_schemas import schemas
from utils.config_utils import get_config
from utils.user_utils import (
	create_user,
	set_user_admin
)

###############################################################################

CONFIG = get_config('initial_user.cfg')
INITIAL_USER_CONFIG = CONFIG['initial_user']
INITIAL_USER = schemas.UserCreate(
	username=INITIAL_USER_CONFIG['username'],
	first_name=INITIAL_USER_CONFIG['first_name'],
	last_name=INITIAL_USER_CONFIG['last_name'],
	email=INITIAL_USER_CONFIG['email'],
	password=INITIAL_USER_CONFIG['password']
)

###############################################################################

def create_initial_user():
	'''Create the initial user'''
	session = session_local()
	models.Base.metadata.create_all(bind=engine)
	user = create_user(database=session, user=INITIAL_USER)
	set_user_admin(database=session, user_id=user.user_id, admin=True)

###############################################################################

create_initial_user()
