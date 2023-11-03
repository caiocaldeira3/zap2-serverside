import gevent
from app import job_queue
from app.services import user as ussr


def job_handler () -> None:
    while True:
        users = ussr.find_connected_users()

        for user in users:
            job_queue.resolve_jobs(user._id)

        job_queue.resolve_jobs(-1, priority=0)

        gevent.sleep(5)