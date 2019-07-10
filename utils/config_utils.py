'''
FastAPI Demo

Main Utils
'''
# Standard Imports
import os.path

# PyPi Imports
import configparser

###############################################################################

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = 'configuration'

###############################################################################

def get_config(config_file: str):
	'''Get config data'''
	config_location = os.path.join(ROOT_PATH, CONFIG_PATH, config_file)
	config = configparser.ConfigParser()
	config.read(config_location)
	return config
