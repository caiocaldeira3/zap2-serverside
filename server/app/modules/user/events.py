from typing import Union

from app import job_queue, sio
# Import module models (i.e. Organization)
from app.models.user import User
from app.services import user as ussr
# Import Util Modules
from app.util import api
from app.util.authentication import authenticate_source, authenticate_user
from app.util.jobs import ConfirmCreateChatJob, ConfirmMessageJob
from flask_socketio import ConnectionRefusedError, emit

RequestData = Union[str, dict[str, str]]

@sio.on("create-chat")
@authenticate_source()
@authenticate_user()
def handle_create_chat (sid: str, data: dict[str, RequestData]) -> None:
    try:
        owner = ussr.find_with_telephone(data["owner"]["telephone"])
        users = ussr.find_many(data["users"])

        data.pop("users", None)
        for user in users:
            opkeys = user.opkeys[ : 2 ]
            api.create_chat(owner, user, opkeys, data)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError

@sio.on("confirm-create-chat")
@authenticate_source()
@authenticate_user()
def handle_confirm_create_chat (sid: str, data: dict[str, RequestData]) -> None:
    try:
        owner: User = ussr.find_with_telephone(data["owner"]["telephone"])
        user_tel = data["user"]["telephone"]

        resp_data = {
            "status": "ok",
            "msg": f"Chat created between users {owner.telephone} and {user_tel}",
            "data": data
        }

        if owner.socket_id is None:
            job_queue.add_job(owner._id, 2, ConfirmCreateChatJob, resp_data)

            return

        try:
            emit("confirm-create-chat", resp_data, to=owner.socket_id)

        except ConnectionRefusedError:
            job_queue.add_job(owner._id, 2, ConfirmCreateChatJob, resp_data)


    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError

@sio.on("message")
@authenticate_source()
@authenticate_user()
def handle_message (sid: str, data: dict[str, RequestData]) -> None:
    try:
        user = ussr.find_with_telephone(data["receiver"]["telephone"])
        api.send_message(user, data)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError

@sio.on("confirm-message")
@authenticate_source()
@authenticate_user()
def handle_confirm_message (sid: str, data: dict[str, RequestData]) -> None:
    try:
        sender: User = ussr.find_with_telephone(data["sender"]["telephone"])
        rcv_tel = data["receiver"]["telephone"]

        resp_data = {
            "status": "ok",
            "msg": f"Message sent from {sender.telephone} to {rcv_tel}",
            "data": data
        }

        if sender.socket_id is None:
            print("Queueing confirm message due to lack of devices")
            job_queue.add_job(sender._id, 2, ConfirmMessageJob, resp_data)

            return

        try:
            emit("confirm-message", resp_data, to=sender.socket_id)

        except ConnectionRefusedError:
            job_queue.add_job(sender._id, 2, ConfirmMessageJob, resp_data)

    except Exception as exc:
        print(exc)

        raise ConnectionRefusedError
