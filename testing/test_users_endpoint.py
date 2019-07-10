'''
Test FastAPI Demo

/users
'''
# Standard Imports
import unittest

# PyPi Imports

# Local Imports
from testing.TestFastAPI import TestFastAPI
from utils.config_utils import get_config
import utils.user_utils as user_utils

###############################################################################

CONFIG = get_config('testing.cfg')
TESTING = CONFIG['testing']

##############################################################################
# Testing class
##############################################################################
class TestUsersEndpoint(TestFastAPI):
	'''Test Validator Functions'''
	def __init__(self, *args, **kwargs): #pylint: disable=W0235
		super(TestUsersEndpoint, self).__init__(*args, **kwargs)
		self.remove_untaken_usernames()

	def __del__(self):
		self.remove_untaken_usernames()

	def remove_untaken_usernames(self):
		'''Clean up users created during user_creation tests'''
		untaken_usernames = ['untaken_username', 'untaken_username2', 'untaken_username3']
		for untaken_username in untaken_usernames:
			user = user_utils.get_user_by_username(self.session, untaken_username)
			if user:
				user_utils.delete_user(self.session, user.user_id)

	def test_get_users(self):
		'''Test if REST API get:/users/ endpoint functions correctly'''
		test_dict = {
			'http_method': 'get',
			'path': '/users/',
			'test_cases': [
				{
					'test_case_description': 'user_list_returned',
					'http_status': 200,
					'header_params': self.regular_token,
					'message': 'User list not returned'
				}
			]
		}
		self.template_test_endpoint_cases(test_dict=test_dict)

	def test_create_user(self):
		'''Test if REST API post:/users/ endpoint functions correctly'''
		test_dict = {
			'http_method': 'post',
			'path': '/users/',
			'test_cases': [
				{
					'test_case_description': 'new_user_returned',
					'http_status': 200,
					'header_params': self.admin_token,
					'body_params': {
						"username": "untaken_username",
						"first_name": "Test",
						"last_name": "User",
						"email": "untaken_username@test.ca",
						"password": "string"
					},
					'message': 'New user not returned'
				},
				{
					'test_case_description': 'insufficient_privilege',
					'http_status': 403,
					'expected_data': {
						'detail': r'^Authenticated user lacks administrative privileges$'
					},
					'header_params': self.regular_token,
					'body_params': {
						"username": 'untaken_username2',
						"first_name": "Test",
						"last_name": "User",
						"email": "untaken_username2@test.ca",
						"password": "string"
					},
					'message': 'Insufficient priviledge not returned'
				},
				{
					'test_case_description': 'username_unavailable',
					'http_status': 409,
					'expected_data': {
						'detail': r'^Username already registered$'
					},
					'header_params': self.admin_token,
					'body_params': {
						"username": TESTING['regular_user'],
						"first_name": "Test",
						"last_name": "User",
						"email": "untaken_username3@test.ca",
						"password": "string"
					},
					'message': 'Username was not rejected as duplicate'
				},
				{
					'test_case_description': 'invalid_email',
					'http_status': 422,
					'header_params': self.admin_token,
					'body_params': {
						"username": 'untaken_username4',
						"first_name": "Test",
						"last_name": "User",
						"email": "bademail",
						"password": "string"
					},
					'message': 'Email was not rejected as badly formed'
				}
			]
		}
		self.template_test_endpoint_cases(test_dict=test_dict)

	def test_get_user(self):
		'''Test if REST API get:/users/{user_id} endpoint functions correctly'''
		test_dict = {
			'http_method': 'get',
			'path': '/users/{user_id}',
			'test_cases': [
				{
					'test_case_description': 'user_returned',
					'http_status': 200,
					'header_params': self.regular_token,
					'path_params': {"user_id": self.regular_user.user_id},
					'message': 'User not returned'
				},
				{
					'test_case_description': 'no_such_user',
					'http_status': 422,
					'expected_data': {
						'detail': r'^No such user_id$'
					},
					'header_params': self.regular_token,
					'path_params': {"user_id": -1},
					'message': 'no_such_user error not returned'
				}
			]
		}
		self.template_test_endpoint_cases(test_dict=test_dict)

	def test_update_user(self):
		'''Test if REST API put:/users/{user_id} endpoint functions correctly'''
		test_dict = {
			'http_method': 'put',
			'path': '/users/{user_id}',
			'test_cases': [
				{
					'test_case_description': 'admin_updates_user',
					'http_status': 200,
					'header_params': self.admin_token,
					'path_params': {"user_id": self.regular_user.user_id},
					'body_params': {
						"first_name": "Regular",
						"last_name": "User",
						"email": "regular_user@test.ca",
					},
					'message': 'User not updated'
				},
				{
					'test_case_description': 'insufficient_privilege',
					'http_status': 403,
					'expected_data': {
						'detail': r'^Authenticated user lacks administrative privileges$'
					},
					'header_params': self.regular_token,
					'path_params': {"user_id": self.inactive_user.user_id},
					'body_params': {
						"first_name": "Inactive",
						"last_name": "User",
						"email": "inactive_user@test.ca",
					},
					'message': 'Forbidden was not returned'
				},
				{
					'test_case_description': 'no_such_user',
					'http_status': 422,
					'expected_data': {
						'detail': r'^No such user_id$'
					},
					'header_params': self.admin_token,
					'path_params': {"user_id": -1},
					'body_params': {
						"first_name": "Test",
						"last_name": "User",
						"email": "untaken_username5@test.ca",
					},
					'message': 'no_such_user error not returned'
				}
			]
		}
		self.template_test_endpoint_cases(test_dict=test_dict)

	def test_delete_user(self):
		'''Test if REST API delete:/users/{user_id} endpoint functions correctly'''
		test_user = self.get_test_user(TESTING['test_user'], TESTING['test_user_password'])
		# 403 is first because otherwise there would be no user for the 200 case to delete
		test_dict = {
			'http_method': 'delete',
			'path': '/users/{user_id}',
			'test_cases': [
				{
					'test_case_description': 'insufficient_privilege',
					'http_status': 403,
					'expected_data': {
						'detail': r'^Authenticated user lacks administrative privileges$'
					},
					'header_params': self.regular_token,
					'path_params': {"user_id": test_user.user_id},
					'message': 'Forbidden was not returned'
				},
				{
					'test_case_description': 'admin_deletes_user',
					'http_status': 200,
					'header_params': self.admin_token,
					'path_params': {"user_id": test_user.user_id},
					'message': 'User not deleted'
				},
				{
					'test_case_description': 'no_such_user',
					'http_status': 422,
					'expected_data': {
						'detail': r'^No such user_id$'
					},
					'header_params': self.admin_token,
					'path_params': {"user_id": -1},
					'message': 'no_such_user error not returned'
				}
			]
		}
		self.template_test_endpoint_cases(test_dict=test_dict)

	def test_set_password(self):
		'''Test if REST API put:/users/{user_id}/set_password endpoint functions correctly'''
		test_user = self.get_test_user(TESTING['test_user'], TESTING['test_user_password'])
		test_token = self.get_authentication_token(TESTING['test_user'], 30)
		test_dict = {
			'http_method': 'put',
			'path': '/users/{user_id}/set_password',
			'test_cases': [
				{
					'test_case_description': 'admin_sets_password',
					'http_status': 200,
					'header_params': self.admin_token,
					'path_params': {"user_id": test_user.user_id},
					'query_params': {"password": "different_password"},
					'message': 'User password not changed'
				},
				{
					'test_case_description': 'user_sets_own_password',
					'http_status': 200,
					'header_params': test_token,
					'path_params': {"user_id": test_user.user_id},
					'query_params': {"password": "different_password"},
					'message': 'Self-User password not changed'
				},
				{
					'test_case_description': 'insufficient_privilege',
					'http_status': 403,
					'expected_data': {
						'detail': r'^Authenticated user lacks administrative privileges$'
					},
					'header_params': self.regular_token,
					'path_params': {"user_id": test_user.user_id},
					'query_params': {"password": "different_password"},
					'message': 'Forbidden was not returned'
				},
				{
					'test_case_description': 'no_such_user',
					'http_status': 422,
					'expected_data': {
						'detail': r'^No such user_id$'
					},
					'header_params': self.admin_token,
					'path_params': {"user_id": -1},
					'query_params': {"password": "different_password"},
					'message': 'no_such_user error not returned'
				}
			]
		}
		self.template_test_endpoint_cases(test_dict=test_dict)

	def test_set_admin(self):
		'''Test if REST API put:/users/{user_id}/set_admin endpoint functions correctly'''
		test_user = self.get_test_user(TESTING['test_user'], TESTING['test_user_password'])
		test_dict = {
			'http_method': 'put',
			'path': '/users/{user_id}/set_admin',
			'test_cases': [
				{
					'test_case_description': 'admin_sets_admin',
					'http_status': 200,
					'header_params': self.admin_token,
					'path_params': {"user_id": test_user.user_id},
					'query_params': {"admin": False},
					'message': 'User admin flag not changed'
				},
				{
					'test_case_description': 'insufficient_privilege',
					'http_status': 403,
					'expected_data': {
						'detail': r'^Authenticated user lacks administrative privileges$'
					},
					'header_params': self.regular_token,
					'path_params': {"user_id": test_user.user_id},
					'query_params': {"admin": False},
					'message': 'Forbidden was not returned'
				},
				{
					'test_case_description': 'admin_deprivileging',
					'http_status': 403,
					'expected_data': {
						'detail': r'^You may not change your own administrative privileges or active status$'
					},
					'header_params': self.admin_token,
					'path_params': {"user_id": self.admin_user.user_id},
					'query_params': {"admin": True},
					'message': 'Admin could change own admin privilege'
				},
				{
					'test_case_description': 'no_such_user',
					'http_status': 422,
					'expected_data': {
						'detail': r'^No such user_id$'
					},
					'header_params': self.admin_token,
					'path_params': {"user_id": -1},
					'query_params': {"admin": False},
					'message': 'no_such_user error not returned'
				}
			]
		}
		self.template_test_endpoint_cases(test_dict=test_dict)

	def test_set_active(self):
		'''Test if REST API put:/users/{user_id}/set_active endpoint functions correctly'''
		test_user = self.get_test_user(TESTING['test_user'], TESTING['test_user_password'])
		test_dict = {
			'http_method': 'put',
			'path': '/users/{user_id}/set_active',
			'test_cases': [
				{
					'test_case_description': 'admin_sets_active',
					'http_status': 200,
					'header_params': self.admin_token,
					'path_params': {"user_id": test_user.user_id},
					'query_params': {"active": True},
					'message': 'User active flag not changed'
				},
				{
					'test_case_description': 'insufficient_privilege',
					'http_status': 403,
					'expected_data': {
						'detail': r'^Authenticated user lacks administrative privileges$'
					},
					'header_params': self.regular_token,
					'path_params': {"user_id": test_user.user_id},
					'query_params': {"active": True},
					'message': 'Forbidden was not returned'
				},
				{
					'test_case_description': 'admin_deprivileging',
					'http_status': 403,
					'expected_data': {
						'detail': r'^You may not change your own administrative privileges or active status$'
					},
					'header_params': self.admin_token,
					'path_params': {"user_id": self.admin_user.user_id},
					'query_params': {"active": True},
					'message': 'Admin could change own active state'
				},
				{
					'test_case_description': 'no_such_user',
					'http_status': 422,
					'expected_data': {
						'detail': r'^No such user_id$'
					},
					'header_params': self.admin_token,
					'path_params': {"user_id": -1},
					'query_params': {"active": False},
					'message': 'no_such_user error not returned'
				}
			]
		}
		self.template_test_endpoint_cases(test_dict=test_dict)

#######################################
# Bare main unit test function
#######################################
if __name__ == '__main__':
	unittest.main()
