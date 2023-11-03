import os
from collections.abc import Callable
from functools import wraps

from app import job_queue
from app.models.user import OPKey, User
from app.services import user as ussr
from app.util.crypto import verify_signed_message
from app.util.jobs import AddUserDeviceJob
from flask import request, wrappers
from flask_socketio import ConnectionRefusedError, emit


def authenticate_source () -> wrappers.Response:
    def wrapper (f: Callable) -> wrappers.Response:
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.headers["Param-Auth"] == os.environ["CHAT_SECRET"]:
                return f(request.sid, *args, **kwargs)

            else:
                emit("auth_response", {
                    "status": "failed",
                    "msg": "Unable to authenticate connection source"
                })

                raise ConnectionRefusedError

        return decorated

    return wrapper

def ensure_user () -> wrappers.Response:
    def wrapper (f: Callable) -> wrappers.Response:
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.headers.get("Signed-Message", None) is not None:
                try:
                    sid, data = args
                    user = ussr.find_with_telephone(data["telephone"])
                    sgn_message = request.headers["Signed-Message"]
                    verify_signed_message(user, sgn_message)

                    job_queue.add_job(-1, 0, AddUserDeviceJob, {"user_id": user._id, "sid": sid})

                    return f(*args, "ok", **kwargs)

                except Exception as exc:
                    print(exc)
                    emit("auth_response", {
                        "status": "failed",
                        "msg": "Unable to authenticate signed message"
                    })

                    raise ConnectionRefusedError

            else:
                try:
                    sid, auth_data = args

                    user = User(
                        name=auth_data["name"],
                        id_key=auth_data["id_key"],
                        sgn_key=auth_data["sgn_key"],
                        ed_key=auth_data["ed_key"],
                        devices=sid,
                        opkeys=[
                            OPKey(key_idx=opkey["id"], opkey=opkey["key"])
                            for opkey in auth_data["opkeys"]
                        ],
                        telephone=auth_data["telephone"],
                        desc=auth_data.get("description", "default user")
                    )

                    ussr.insert_user(user)

                    return f(sid, {
                        "telephone": user.telephone
                    }, "created", **kwargs)

                except Exception as exc:
                    print(exc)
                    emit("auth_response", {
                        "status": "failed",
                        "msg": "Unable to create a new user"
                    })

                    raise ConnectionRefusedError

        return decorated

    return wrapper

def authenticate_user () -> wrappers.Response:
    def wrapper (f: Callable) -> wrappers.Response:
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                sid, data = args
                sgn_message = data["Signed-Message"]
                user = ussr.find_with_telephone(data["telephone"])

                data = data.pop("body")
                verify_signed_message(user, sgn_message)

                return f(sid, data, **kwargs)

            except Exception as exc:
                print(exc)
                emit("auth_response", {
                    "status": "failed",
                    "msg": "Unable to authenticate signed message"
                })

                raise ConnectionRefusedError

        return decorated

    return wrapper
