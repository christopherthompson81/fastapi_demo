'''
Test FastAPI Demo

/token
'''
# Standard Imports
import unittest

# PyPi Imports

# Local Imports
from testing.TestFastAPI import TestFastAPI
from utils.config_utils import get_config

###############################################################################

CONFIG = get_config('testing.cfg')
TESTING = CONFIG['testing']

##############################################################################
# Testing class
##############################################################################
class TestTokenEndpoint(TestFastAPI):
	'''Test Validator Functions'''
	def __init__(self, *args, **kwargs): #pylint: disable=W0235
		super(TestTokenEndpoint, self).__init__(*args, **kwargs)

	def test_token_endpoint(self):
		'''Test if REST API /token endpoint functions correctly'''
		test_dict = {
			'http_method': 'post',
			'path': '/token',
			'test_cases': [
				{
					'test_case_description': 'token_issued',
					'http_status': 200,
					'expected_data': {
						"access_token": r".+",
						"token_type": "bearer"
					},
					'form_params': {
						"username": TESTING['regular_user'],
						"password": TESTING['regular_user_password']
					},
					'message': 'Authorized Token not returned when using valid credentials'
				},
				{
					'test_case_description': 'authorization_failure',
					'http_status': 401,
					'expected_data': {
						"detail": r"^Incorrect username or password$"
					},
					'form_params': {
						"username": TESTING['regular_user'],
						"password": 'bad_password'
					},
					'message': 'Authorization failure not returned when using invalid credentials'
				},
				{
					'test_case_description': 'inactive_user',
					'http_status': 401,
					'expected_data': {
						"detail": r"^Inactive user$"
					},
					'form_params': {
						"username": TESTING['inactive_user'],
						"password": TESTING['inactive_user_password']
					},
					'message': 'Authorization failure not returned when using inactive user'
				}
			]
		}
		# Consider adding additional tests:
		# * Inactive User
		# * User deleted since last auth
		self.template_test_endpoint_cases(test_dict=test_dict)

	def test_token_refresh_endpoint(self):
		'''Test if REST API /token/refresh endpoint functions correctly'''
		test_dict = {
			'http_method': 'post',
			'path': '/token/refresh',
			'test_cases': [
				{
					'test_case_description': 'new_token_issued',
					'http_status': 200,
					'expected_data': {
						"access_token": r".+",
						"token_type": "bearer"
					},
					'header_params': self.regular_token,
					'message': 'New Authorized Token not returned when using valid and unexpired token'
				},
				{
					'test_case_description': 'bad_token',
					'http_status': 400,
					'expected_data': {
						"detail": r"^JWT could not be processed$"
					},
					'header_params': {"Authorization": 'Bearer bad_token'},
					'message': 'Server did not reject a bad token'
				},
				{
					'test_case_description': 'not_authenticated',
					'http_status': 401,
					'expected_data': {
						"detail": r"^Not authenticated$"
					},
					'message': 'Server did not return unauthorized when no authentication token was used'
				},
				{
					'test_case_description': 'expired_token',
					'http_status': 401,
					'expected_data': {
						"detail": r"^Token Expired\. Reauthenticate$"
					},
					'header_params': self.expired_token,
					'message': 'Server did not return unauthorized when a non-refreshable expired token was used'
				},
				{
					'test_case_description': 'inactive_user_token',
					'http_status': 401,
					'expected_data': {
						"detail": r"^Inactive user$"
					},
					'header_params': self.inactive_token,
					'message': 'Server did not return unauthorized when a non-refreshable inactive user token was used'
				}
			]
		}
		# Consider adding additional tests:
		# * Inactive User
		# * User deleted since last auth
		self.template_test_endpoint_cases(test_dict=test_dict)

#######################################
# Bare main unit test function
#######################################
if __name__ == '__main__':
	unittest.main()
