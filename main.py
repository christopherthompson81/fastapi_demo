'''
FastAPI Demo

Main application
'''
# Standard Imports

# PyPi Imports
from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import Response

# Local Imports
import database.models as models
from database.setup import (
	session_local,
	engine
)
from routers import (
	token,
	users
)

###############################################################################

models.Base.metadata.create_all(bind=engine)

app = FastAPI( #pylint: disable=invalid-name
	title="FastAPI Demo",
    description="This is a demo application for FastAPI",
    version="0.0.1"
)

###############################################################################

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
	'''Function to populate requests with a database session'''
	response = Response("Internal server error", status_code=500)
	try:
		request.state.db = session_local()
		response = await call_next(request)
	finally:
		request.state.db.close()
	return response

###############################################################################

app.include_router(
	token.router,
	tags=["token"]
)
app.include_router(
	users.router,
	dependencies=[Depends(token.check_current_user)],
	tags=["users"]
)
