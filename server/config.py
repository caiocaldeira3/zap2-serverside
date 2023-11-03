import os
import sys
from pathlib import Path

import dotenv

base_path = Path(__file__).resolve().parent
dotenv.load_dotenv(base_path / ".env", override=False)

sys.path.append(str(base_path))

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

APP_PORT = int(os.environ.get("PORT", 5000))

# Define the database - we are working with
# SQLite for this example
MONGO_CONN = os.environ["MONGO_CONNECTION_STRING"]
MONGO_DB = os.environ["MONGO_DATABASE"]

DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "W1JKKarQaco3qtBhwfpToqIrK3ATRP9q"

# Secret key for signing cookies
SECRET_KEY = os.environ["SECRET_KEY"]
