import atexit
import dotenv

from pathlib import Path

base_path = Path(__file__).resolve().parent
dotenv.load_dotenv(base_path / ".env", override=False)

from app.models.device import Device

from app import db
from app import sio
from app import flask_app

def exit_handler():
    Device.query.delete()
    db.session.commit()

atexit.register(exit_handler)

if __name__ == '__main__':
    sio.run(flask_app, host="0.0.0.0", use_reloader=False)