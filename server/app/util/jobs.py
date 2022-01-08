import dataclasses as dc

from typing import Union
from flask_socketio import emit, send
from abc import ABCMeta, ABC, abstractmethod

from app.models.user import User

from app.util.exc import (
    NotJobInstance, PriorityRangeError, UserDeviceNotFound
)


from app import sio

RequestData = dict[str, Union[str, dict[str, str]]]
MAX_RETRIES = 5
MIN_PRIORITY = 1
MAX_PRIORITY = 3

@dc.dataclass(init=True)
class Job (ABC):

    user_id: int = dc.field(init=True, default=None)
    data: RequestData = dc.field(init=True, default=None)
    retries: int = dc.field(init=True, default=0)
    priority: int = dc.field(init=True, default=0)

    @abstractmethod
    def solve (self) -> None:
        pass

    def increment_retries (self) -> int:
        self.retries += 1

        return self.retries

    def identify_job_type (self) -> None:
        print(type(self))

class CreateChatJob (Job):
    def solve (self) -> None:
        user = User.query.filter_by(id=self.user_id).one()
        if len(user.devices) == 0:
            raise UserDeviceNotFound

        for device in user.devices:
            emit("create-chat", data=self.data, to=device.socket_id)

class ConfirmCreateChatJob (Job):
    def solve (self) -> None:
        owner = User.query.filter_by(id=self.user_id).one()
        if len(owner.devices) == 0:
            raise UserDeviceNotFound

        for device in owner.devices:
            emit("confirm-create-chat", data=self.data, to=device.socket_id)

class SendMessageJob (Job):
    def solve (self) -> None:
        receiver = User.query.filter_by(id=self.user_id).one()
        if len(receiver.devices) == 0:
            raise UserDeviceNotFound

        for device in receiver.devices:
            emit("send-message", data=self.data, to=device.socket_id)

class ConfirmMessageJob (Job):
    def solve (self) -> None:
        sender = User.query.filter_by(id=self.user_id).one()
        if len(sender.devices) == 0:
            raise UserDeviceNotFound

        for device in sender.devices:
            emit("confirm-message", data=self.data, to=device.socket_id)

Jobs = Union[list[Job], dict[str, list[Job]]]

@dc.dataclass(init=True)
class JobQueue:
    job_dict: dict[int, list[Jobs]] = dc.field(init=False, default_factory=dict)

    def add_job (
        self, user_id: int, priority: int,
        job_class: ABCMeta, data: RequestData = None, retries: int = 0
    ) -> None:
        if not isinstance(job_class(), Job):
            raise NotJobInstance

        job = job_class(user_id, data, priority, retries)

        if self.job_dict.get(user_id, None) is None:
            self.job_dict[user_id] = [ list(), list(), list() ]

        if MIN_PRIORITY <= priority <= MAX_PRIORITY:
            self.job_dict[user_id][priority].append(job)

        else:
            raise PriorityRangeError

    def _resolve_jobs (self, jobs: list[Job]) -> list[Job]:
        failed_jobs = []
        for job in jobs:
            try:
                job.solve()

            except ConnectionRefusedError:
                if job.increment_retries() < MAX_RETRIES:
                    failed_jobs.append(job)

            except UserDeviceNotFound:
                if job.increment_retries() < MAX_RETRIES:
                    failed_jobs.append(job)

            except Exception as exc:
                print(f"Ill formed job of type {type(job)}")
                print(exc)

        return failed_jobs

    def resolve_jobs (self, user_id: int, priority: int = None) -> None:
        if self.job_dict.get(user_id, None) is None:
            return

        elif priority is None:
            for curr_priority in range(MIN_PRIORITY, MAX_PRIORITY):
                self.resolve_jobs(user_id, priority=curr_priority)

            return

        if MIN_PRIORITY <= priority <= MAX_PRIORITY:
            self.job_dict[user_id][priority] = self._resolve_jobs(self.job_dict[user_id][priority])

        else:
            raise PriorityRangeError


        for curr_priority in range(MIN_PRIORITY, MAX_PRIORITY):
            if len(self.job_dict[user_id][priority]) > 0:
                return

        self.job_dict.pop(user_id, None)