'''
FastAPI Demo

Generate a brand new set of config files with new secrets and secure passwords
'''
# Standard Imports
import os

###############################################################################

def generate_database_cfg():
	'''Generate the database config file'''
	database_cfg_template = '''[database]
POSTGRES_URL = 127.0.0.1:5432
POSTGRES_DB = fastapi_demo
POSTGRES_USER = fastapi_demo
POSTGRES_PW = {db_secret}
'''
	return database_cfg_template.format(db_secret=os.urandom(32).hex())

def generate_initial_user_cfg():
	'''Generate the initial user config file'''
	initial_user_cfg_template = '''[initial_user]
username = initial_user
first_name = Initial
last_name = User
email = initial_user@test.ca
password = {initial_user_pw}
'''
	return initial_user_cfg_template.format(initial_user_pw=os.urandom(32).hex())

def generate_security_cfg():
	'''Generate the security config file'''
	security_cfg_template = '''[security]
SECRET_KEY = {api_secret}
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_LEEWAY_SECONDS = 30
'''
	return security_cfg_template.format(api_secret=os.urandom(32).hex())

def generate_testing_cfg():
	'''Generate the security config file'''
	security_cfg_template = '''[testing]
test_user = test_user
test_user_password = {test_user_password}
admin_user = admin_user
admin_user_password = {admin_user_password}
regular_user = regular_user
regular_user_password = {regular_user_password}
inactive_user = inactive_user
inactive_user_password = {inactive_user_password}
'''
	return security_cfg_template.format(
		test_user_password=os.urandom(32).hex(),
		admin_user_password=os.urandom(32).hex(),
		regular_user_password=os.urandom(32).hex(),
		inactive_user_password=os.urandom(32).hex()
	)

def write_config(config_file, contents):
	'''Write out contents to a file'''
	print(contents)
	file_object = open(config_file, 'w')
	file_object.write(contents)

def main():
	'''Main Function'''
	config_dir = 'configuration'
	if not os.path.exists(config_dir):
		os.makedirs(config_dir)
	database_config_file = os.path.join(config_dir, 'database.cfg')
	initial_user_config_file = os.path.join(config_dir, 'initial_user.cfg')
	security_config_file = os.path.join(config_dir, 'security.cfg')
	testing_config_file = os.path.join(config_dir, 'testing.cfg')
	write_config(database_config_file, generate_database_cfg())
	write_config(initial_user_config_file, generate_initial_user_cfg())
	write_config(security_config_file, generate_security_cfg())
	write_config(testing_config_file, generate_testing_cfg())

###############################################################################

main()
