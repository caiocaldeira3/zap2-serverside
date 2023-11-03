import eventlet
# Import flask and template operators
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Import Util Modules
# from app.util.responses import NotFoundError

# Define the WSGI application object
flask_app = Flask(__name__)
CORS(flask_app)

# Configurations
flask_app.config.from_object('config')
sio = SocketIO(flask_app, async_mode="eventlet")

from app.util.jobs import JobQueue

job_queue = JobQueue()

# Import a module / component using its blueprint handler variable (mod_auth)
import app.modules.auth.events
import app.modules.user.events
from app.util.job_handler import job_handler

# Sample HTTP error handling
#@app.errorhandler(404)
#def not_found (error: Exception) -> wrappers.Response:
#    return NotFoundError

eventlet.monkey_patch()
sio.start_background_task(job_handler)
