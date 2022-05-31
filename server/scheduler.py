import datetime
import random
import shelve
import hashlib
from typing import Optional

from persist.db import Session
from settings import FILE_FOR_SAVE_ACTIVE_JOB, PERIOD_ACTIVE_JOB
from entity import ChatRow


class ChatsIsOver(Exception):
    pass


class Scheduler:

    def __init__(self):
        self._chats: list[ChatRow] = list()
        self._sessions: list[Session] = Session.get_sessions()
        self.job_queue = dict()
        self.active_job = shelve.open(FILE_FOR_SAVE_ACTIVE_JOB)

    def validate_job(self, job_id: str, chat_id: int) -> bool:
        if job_id in self.active_job.keys():
            job = self.active_job[job_id]
            return job["chat_id"] == chat_id
        return False

    def complete(self, job_id: str) -> int:
        """
        Убирает из списка выданных заданий задание с идентификатором job_id, позволяя серверу вновь использовать
        чат для которого формировалось указанное задание для формирования нового задания
        :param job_id: id выданного задания
        :return: id чата который был обработан клиентом в текущем задании
        """
        if job_id in self.active_job.keys():
            job = self.active_job[job_id]
            self.active_job.pop(job_id)
            print(f"Job {job_id} completed")
            return job["chat_id"]

    def get_job_by_id(self, job_id: str) -> Optional[dict]:
        if job_id in self.active_job.keys():
            return self.active_job[job_id]
        else:
            return None

    def get_job(self) -> dict:
        session = self._get_session()
        chat = self._get_chat()
        if (session is not None) and (chat is not None):
            session.add_use_count()
            md = hashlib.md5()
            md.update(str(session.session).encode("utf-8"))
            md.update(str(chat.chat_id).encode("utf-8"))
            md.update(str(datetime.datetime.now()).encode("utf-8"))
            job_id = md.hexdigest()
            self.active_job[job_id] = {"session": session,
                                       "chat_id": chat.chat_id,
                                       "date": datetime.datetime.now()
                                       }
            return {
                "job_id": job_id,
                "session": session.session,
                "chat_id": chat.chat_id,
                "chat_link": chat.chat_link,
                "last_message_id": chat.last_message_id
            }
        else:
            return {}

    def set_chats(self, chats: list[ChatRow]) -> None:
        self._chats = chats
        self._garbage_collector()
        for ch in self._chats[:]:
            if self._is_chat_in_process(ch.chat_id):
                self._chats.remove(ch)

    def add_chat(self, chat: ChatRow) -> None:
        self._garbage_collector()
        if not self._is_chat_in_process(chat.chat_id):
            self._chats.append(chat)

    def _garbage_collector(self) -> None:
        for job_id in self.active_job.keys():
            job_date: datetime.datetime = self.active_job[job_id]["date"]
            if (datetime.datetime.now().timestamp() - job_date.timestamp()) > PERIOD_ACTIVE_JOB:
                self.active_job.pop(job_id)
                print(f"Job {job_id} deleted garbage collectors")

    def _get_session(self) -> Optional[Session]:
        random.shuffle(self._sessions)
        for session in self._sessions:
            if session.is_active():
                return session
        self._sessions = Session.get_sessions()
        return None

    def _get_chat(self) -> Optional[ChatRow]:
        if not self._chats:
            raise ChatsIsOver
        self._chats.sort(key=lambda x: x.date_last_update, reverse=True)
        return self._chats.pop()

    def _is_chat_in_process(self, cid: int) -> bool:
        for job_id in self.active_job.keys():
            job = self.active_job[job_id]
            if job["chat_id"] == cid:
                return True
        return False
