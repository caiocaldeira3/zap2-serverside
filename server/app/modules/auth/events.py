from app import job_queue, sio
from app.services import user as ussr
from app.util.authentication import authenticate_source, ensure_user
from flask import request
from flask_socketio import emit


@sio.on("connect")
@authenticate_source()
@ensure_user()
def handle_connect (sid: str, data: dict[str, str], status: str) -> None:
    user = ussr.find_with_telephone(data["telephone"])
    print(f"connect {sid}")
    emit("auth_response", {
        "status": status,
        "msg": "Session Authenticated",
        "data": {
            "user": {
                "id": user._id,
                "telephone": user.telephone
            }
        }
    })

@sio.on("disconnect")
def disconnect () -> None:
    ussr.delete_device(request.sid)
    job_queue.remove_jobs(sid=request.sid)

    print(f"disconnect {request.sid}")
