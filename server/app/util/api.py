from app import job_queue
from app.models.user import OPKey, User
from app.util.jobs import CreateChatJob, SendMessageJob
from flask_socketio import emit, send


def create_chat (owner: User, user: User, opkeys: list[OPKey], req_info: dict) -> None:
    chat_id = req_info["owner"]["chat_id"]
    data = {
        "status": "pending",
        "msg": f"Creating chat {chat_id} between {owner.telephone} and {user.telephone}",
        "data": {
            "owner": {
                "name": owner.name,
                "telephone": owner.telephone,
                "description": owner.desc,
                "chat_id": req_info["owner"]["chat_id"],
                "keys": {
                    "pb_keys": {
                        "IK": owner.id_key,
                        "EK": req_info["EK"],
                    }
                },
            },
            "user": {
                "telephone": user.telephone,
                "used_keys": [ opkeys[0].key_idx, opkeys[1].key_idx ],
                "dh_ratchet": req_info["dh_ratchet"]
            },
            "name": req_info["name"],
        }
    }

    if user.socket_id is None:
        job_queue.add_job(user._id, 1, CreateChatJob, data)

    else:
        try:
            emit("create-chat", data, to=user.socket_id)

        except ConnectionRefusedError as exc:
            print(f"Queueing chat creation between {owner.telephone} and {user.telephone}")
            job_queue.add_job(user._id, 1, CreateChatJob, data)

        except Exception as exc:
            print(exc)

            raise Exception

def send_message (receiver: User, req_info: dict) -> None:
    snd_tel = req_info["sender"]["telephone"]
    data = {
        "status": "pending",
        "msg": f"Sending message from {snd_tel} to {receiver.telephone}",
        "data": req_info
    }

    if receiver.socket_id is None:
        job_queue.add_job(receiver._id, 2, SendMessageJob, data)

    else:
        try:
            send(data, to=receiver.socket_id)

        except ConnectionRefusedError as exc:
            print(f"Queueing send messsage to {receiver.telephone}")
            job_queue.add_job(receiver._id, 2, SendMessageJob, data)

        except Exception as exc:
            print(exc)

            raise Exception