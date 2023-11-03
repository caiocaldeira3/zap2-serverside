import atexit

from gevent import monkey

_ = monkey.patch_all()

import config
from app import flask_app, sio
from app.services import user as ussr


def exit_handler():
    ussr.disconect_users()

atexit.register(exit_handler)

if __name__ == '__main__':
    sio.run(flask_app, host="0.0.0.0", port=config.APP_PORT, use_reloader=False)