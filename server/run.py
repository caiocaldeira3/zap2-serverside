import atexit
import os
import sys
from pathlib import Path

import dotenv

base_path = Path(__file__).resolve().parent
dotenv.load_dotenv(base_path / ".env", override=False)

sys.path.append(str(base_path))

from app import flask_app, sio
from app.services import user as ussr


def exit_handler():
    ussr.disconect_users()

atexit.register(exit_handler)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    sio.run(flask_app, host="0.0.0.0", port=port, use_reloader=False)