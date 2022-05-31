from entity import UserRow, ChatMessage
from scheduler import Scheduler, ChatsIsOver
from persist.db import SessionDBSQLite, CHTKDBPostgresImpl, CHTKDBSQLiteImpl
from settings import SQLITE_DATABASE, POSTGRES_DATABASE


class InputJSONNotValid(Exception):
    pass


class JobNotValid(Exception):
    pass


class Manager:

    def __init__(self, database_type: str = SQLITE_DATABASE):
        if database_type == POSTGRES_DATABASE:
            self._chtk_db = CHTKDBPostgresImpl()
        else:
            self._chtk_db = CHTKDBSQLiteImpl()
        self._session_db = SessionDBSQLite()
        self._scheduler = Scheduler()
        self._scheduler.set_chats(self._chtk_db.get_chats())

    def add_users(self, chat_id: int, users: list) -> None:
        array: list[UserRow] = list()
        for item in users:
            array.append(UserRow(
                user_id=item.get("userid"),
                first_name=item.get("first_name"),
                is_bot=item.get("is_bot", False),
                username=item.get("username"),
                last_name=item.get("second_name"),
                phone=item.get("phone")))
        self._chtk_db.add_all_users(chat_id, array)

    def add_messages(self, chat_id: int, messages: list) -> None:
        array: list[ChatMessage] = list()
        for item in messages:
            array.append(ChatMessage(
                message_id=item.get("id"),
                chat_id=chat_id,
                user_id=item.get("user"),
                timestamp=item.get("timestamp"),
                content=item.get("content")["data"],
                content_type=item.get("content")["type"],
                frw_message_id=item.get("frw_message_id", None)
            ))
        self._chtk_db.add_all_messages(chat_id, array)

    def add_sessions(self, sessions: list[dict]) -> None:
        self._session_db.add_sessions(sessions)

    def get_job(self) -> dict:
        try:
            return self._scheduler.get_job()
        except ChatsIsOver:
            self._scheduler.set_chats(self._chtk_db.get_chats())
            return {}

    def complete_job(self, job_id: str, chat_id: int):
        if self._scheduler.validate_job(job_id, chat_id):
            self._scheduler.complete(job_id=job_id)
        else:
            raise JobNotValid

    def _validate_input(self, input: dict, type_input: str) -> bool:
        if type_input == "user":
            return True
