'''
Test FastAPI Demo

Common Classes
'''
# Standard Imports
from datetime import timedelta
import re
import unittest
import urllib

# PyPi Imports
from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient

# Local Imports
from database.setup import session_local
from data_schemas import schemas
from routers import (
	token,
	users
)
from utils.config_utils import get_config
from utils.token_utils import create_access_token
import utils.user_utils as user_utils

###############################################################################

CONFIG = get_config('testing.cfg')
TESTING = CONFIG['testing']
PASS_MSG = 'Parameters meant to pass the test produced negative result'

###############################################################################
# Testing class
###############################################################################
class TestFastAPI(unittest.TestCase):
	'''Template class for testing a PostgreSQL database'''
	def __init__(self, *args, **kwargs):
		super(TestFastAPI, self).__init__(*args, **kwargs)
		self.app = FastAPI()
		self.setup_fastapi_app()
		self.client = TestClient(self.app)
		self.session = session_local()
		self.admin_user = self.get_test_user(TESTING['admin_user'], TESTING['admin_user_password'])
		user_utils.set_user_admin(database=self.session, user_id=self.admin_user.user_id, admin=True)
		self.admin_token = self.get_authentication_token(TESTING['admin_user'], 30)
		self.regular_user = self.get_test_user(TESTING['regular_user'], TESTING['regular_user_password'])
		self.regular_token = self.get_authentication_token(TESTING['regular_user'], 30)
		self.inactive_user = self.get_test_user(TESTING['inactive_user'], TESTING['inactive_user_password'])
		user_utils.set_user_active(database=self.session, user_id=self.inactive_user.user_id, active=False)
		self.inactive_token = self.get_authentication_token(TESTING['inactive_user'], 30)
		self.expired_token = self.get_authentication_token(TESTING['regular_user'], -30)

	def __del__(self):
		self.session.close()

	def setup_fastapi_app(self):
		'''Setup the FastAPI application'''
		@self.app.middleware("http")
		async def db_session_middleware(request: Request, call_next): #pylint: disable=unused-variable
			'''Function to populate requests with a database session'''
			response = Response("Internal server error", status_code=500)
			try:
				request.state.db = session_local()
				response = await call_next(request)
			finally:
				request.state.db.close()
			return response
		self.app.include_router(
			token.router,
			tags=["token"]
		)
		self.app.include_router(
			users.router,
			dependencies=[Depends(token.check_current_user)],
			tags=["users"]
		)

	def remove_test_usernames(self):
		'''Clean up users created during user_creation tests'''
		untaken_usernames = ['admin_user', 'regular_user', 'inactive_user']
		for untaken_username in untaken_usernames:
			user = user_utils.get_user_by_username(self.session, untaken_username)
			if user:
				user_utils.delete_user(self.session, user.user_id)

	def get_test_user(self, username: str, password: str):
		'''Get or create a user for testing purposes'''
		user = user_utils.get_user_by_username(self.session, username=username)
		if not user:
			user_data = schemas.UserCreate(
				username=username,
				first_name='Test',
				last_name='User',
				email='{username}@test.ca'.format(username=username),
				password=password
			)
			return user_utils.create_user(database=self.session, user=user_data)
		else:
			return user

	def get_authentication_token(self, username: str, expires_in: int):
		'''Get an authorized access token for testing'''
		user = user_utils.get_user_by_username(self.session, username)
		token_str = create_access_token(
			data={"user_id": user.user_id},
			expires_delta=timedelta(minutes=expires_in)
		)
		token_dict = {
			"Authorization": 'Bearer ' + token_str.decode('utf-8')
		}
		return token_dict

	###########################################################################
	# Test templates
	###########################################################################

	def template_test_endpoint(
		self,
		path: str,
		description: str,
		http_method: str = 'get',
		expected_status: int = 200,
		expected_data: dict = None,
		header_params: dict = None,
		path_params: dict = None,
		query_params: dict = None,
		form_params: dict = None,
		body_params: dict = None,
		message: str = PASS_MSG
	):
		'''Unit Test template to test an endpoint for a specific outcome'''
		formatted_path = path.format(**path_params) if path_params else path
		if query_params:
			formatted_path += '?' + urllib.parse.urlencode(query_params)
		params = dict()
		if header_params:
			params['headers'] = header_params
		if body_params:
			params['json'] = body_params
		if form_params:
			params['data'] = form_params
		#print(formatted_path, params)
		if http_method == 'get':
			response = self.client.get(formatted_path, **params)
		elif http_method == 'post':
			response = self.client.post(formatted_path, **params)
		elif http_method == 'put':
			response = self.client.put(formatted_path, **params)
		elif http_method == 'delete':
			response = self.client.delete(formatted_path, **params)
		elif http_method == 'options':
			response = self.client.options(formatted_path, **params)
		elif http_method == 'head':
			response = self.client.head(formatted_path, **params)
		elif http_method == 'patch':
			response = self.client.patch(formatted_path, **params)
		else:
			self.fail('Unprocessable HTTP method. Revise test')
		bad_status_template = '[{description}] Got HTTP Status: {status} instead of expected: {expected_status}: {error}'
		bad_status_message = bad_status_template.format(
			description=description,
			status=str(response.status_code),
			expected_status=str(expected_status),
			error=str(response.json())
		)
		self.assertTrue(response.status_code == expected_status, msg=bad_status_message)
		if expected_data:
			response_dict = response.json()
			for key in expected_data:
				self.assertTrue(re.match(expected_data[key], response_dict[key]), msg=message)

	def template_test_endpoint_cases(self, test_dict: dict):
		'''Unit Test template to test all the different possible endpoint HTTP statuses'''
		for test_case in test_dict['test_cases']:
			self.template_test_endpoint(
				http_method=test_dict['http_method'],
				path=test_dict['path'],
				description=test_case['test_case_description'],
				expected_status=test_case['http_status'],
				expected_data=test_case.get('expected_data', None),
				header_params=test_case.get('header_params', None),
				path_params=test_case.get('path_params', None),
				query_params=test_case.get('query_params', None),
				form_params=test_case.get('form_params', None),
				body_params=test_case.get('body_params', None),
				message=test_case['message']
			)
