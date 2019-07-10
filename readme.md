FastAPI Demo
====================

FastAPI demo is a minimal implementation of a full-featured FastAPI instance.

FastAPI:
* https://fastapi.tiangolo.com/ 
* https://github.com/tiangolo/fastapi

While there is a project generator that Tiangolo provided, it included more than just the basics. There is also a very helpful tutorial, but that is a piecemeal approach.

This project occupies the space between the tutorial and the project generator and is a quickstart for your API. There is just enough code to securely control access using JWT and OAuth2, persist data to a production-ready database (PostgreSQL), and conduct unit testing. There should be sufficient code to understand how to combine the elements of the tutorial, but not an overwhelming amount.

# Configure initial setup

## Install PostgreSQL server

* https://www.postgresql.org/download/macosx/

Download and follow instructions

## Install pgAdmin

* https://www.pgadmin.org/download/

Download and follow instructions

## Install Python

* https://www.python.org/downloads/

Download and follow instructions

## Set up the Python environment

* Install pipenv
    > pip install pipenv
* Use pipenv to create virtual environment and install dependencies
    > pipenv install
* Launch the virtual environment
    > pipenv shell
* Generate configuration files
    > python generate_config.py

## Create FastAPI Demo Database

* Launch a pgAdmin window
* Create a user
    * Name: fastapi_demo
    * Password: look in configuration/database.cfg and use the POSTGRES_PW value
    * Privileges: Can Login
* Create a database
    * Name: fastapi_demo
    * Owner: fastapi_demo
    * Security:
        * Grantee: fastapi_demo
        * Privileges: ALL (without grant option)
* Create a separate server instance in pgAdmin
    * Use the fastapi_demo user and password to create a new "server" item in pgAdmin
    * This makes sure that the database admin window will generate the exactly the same errors and won't create things that can't be accessed.

## Run the Demo

* Add the initial user
    * Update the configuration/initial_user.cfg file as needed
    > python create_initial_user.py
* Launch the server
    > uvicorn main:app --reload
* Connect
    * Browse to http://127.0.0.1:8000/docs

## Testing your code

You should maintain the testing code as you build out your API. Running the current tests is done by calling:
> python run_tests.py

All of the existing endpoints have tests written for them. The unittest framework is relatively easy and the examples are data-driven, so they should be easy to read.