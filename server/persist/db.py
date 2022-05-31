import datetime

from persist.persist import *
from entity import ChatRow, ChatMessage, UserRow


class SQLiteDB:

    @staticmethod
    def _get_connection() -> sqlite3.Connection:
        try:
            connection = sqlite3.connect(SESSION_DB)
            return connection
        except Exception as e:
            logger.critical("ERROR: ", exc_info=e)


class SessionDBSQLite(SQLiteDB):

    def __init__(self):
        self._validate_db()

    def _validate_db(self):
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS tlgsessions(
                session        varchar(512) NOT NULL PRIMARY KEY,
                start_use_time timestamp,
                use_count      integer);
            """)
            connection.commit()

    def add_session(self, session_str: str):
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO tlgsessions(session, start_use_time, use_count) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                (session_str, datetime.datetime.now(), 0))
            connection.commit()

    def add_sessions(self, sessions: list[dict]):
        with self._get_connection() as connection:
            cursor = connection.cursor()
            for session in sessions:
                cursor.execute(
                    "INSERT INTO tlgsessions(session, start_use_time, use_count) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                    (session["session"], datetime.datetime.now(), 0))
            connection.commit()
            print(f"Session added:  {session}")

    def update(self, psession: dict) -> bool:
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "update tlgsessions set (start_use_time, use_count) = (?, ?) where session=?",
                (psession["start_use_time"],
                 psession["use_count"],
                 psession["session"]))
            return True

    def get_sessions(self) -> list:
        result = list()
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("select * from tlgsessions")
            for session_row in cursor:
                result.append(Session(session_row[0], datetime.datetime.fromisoformat(session_row[1]), session_row[2]))
        connection.commit()
        return result


class Session:
    db = SessionDBSQLite()

    @classmethod
    def get_sessions(cls) -> list:
        return cls.db.get_sessions()

    def __init__(self, session_str: str = "No valid session. Valid session cannot be created now! Try later.",
                 start_use_time: datetime = datetime.datetime.now(), use_count: int = 0):
        self._session: str = session_str
        self._use_count: int = use_count
        self._start_use_time: datetime = start_use_time
        self._session_status: bool = True if use_count < USE_LIMIT-1 else False

    def __str__(self):
        return f"Session: {self._session}; Date: {self._start_use_time}; Count: {self._use_count}; Status: {'Active' if self.is_active() else 'Disable'};"

    def _db_sync(self):
        if self._use_count >= USE_LIMIT-1:
            self._session_status = False
        if self._session_status:
            self.__class__.db.update({
                "session": self._session,
                "start_use_time": self._start_use_time,
                "use_count": self._use_count
            })

    @property
    def session(self) -> str:
        return self._session

    @property
    def use_count(self) -> int:
        return self._use_count

    @use_count.setter
    def use_count(self, count: int):
        self._use_count = count
        self._db_sync()

    def add_use_count(self):
        self._use_count += 1
        self._db_sync()

    def is_active(self) -> bool:
        if not self._session_status:
            if (datetime.datetime.now().timestamp() - self._start_use_time.timestamp()) > PERIOD_BETWEEN_USE_SESSION:
                print(f"Session {self._session} relife")
                self._start_use_time = datetime.datetime.now()
                self._session_status = True
                self._use_count = 0
                self._db_sync()
        return self._session_status


class BaseDB(metaclass=ABCMeta):

    def __init__(self):
        self._QUERY_SELECT_LAST_MESSAGE_DATETIME = QUERY_SELECT_LAST_MESSAGE_DATETIME
        self._QUERY_INSERT_INTO_USER = QUERY_INSERT_INTO_USER
        self._QUERY_INSERT_USER_INFO = QUERY_INSERT_USER_INFO
        self._QUERY_INSERT_INTO_USERS_CHATS = QUERY_INSERT_INTO_USERS_CHATS
        self._QUERY_INSERT_INTO_CHAT_MESSAGES = QUERY_INSERT_INTO_CHAT_MESSAGES
        self._QUERY_UPDATE_CHAT_LAST_MESSAGE_INFO = QUERY_UPDATE_CHAT_LAST_MESSAGE_INFO
        self._QUERY_CHECK_USER_EXIST = QUERY_CHECK_USER_EXIST
        self._QUERY_CHECK_CHAT_EXIST = QUERY_CHECK_CHAT_EXIST
        self._QUERY_SELECT_ALL_CHATS = QUERY_SELECT_ALL_CHATS
        self._QUERY_SELECT_CHAT_BY_ID = QUERY_SELECT_CHAT_BY_ID
        self._QUERY_SET_LAST_CHECK_IN_CHAT = QUERY_SET_LAST_CHECK_IN_CHAT
        self._QUERY_UPDATE_USER_LAST_ID = QUERY_UPDATE_USER_LAST_ID
        self._queries_prepare()

    @abstractmethod
    def _queries_prepare(self) -> None:
        pass

    @abstractmethod
    def _get_connection(self) -> Union[psycopg2.extensions.connection, sqlite3.Connection, MockConnection]:
        pass

    def _get_last_message_dt(self, chat_id: int) -> Optional[datetime.datetime]:
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(self._QUERY_SELECT_LAST_MESSAGE_DATETIME, (chat_id,))
            for row in cursor:
                last_message_ts = ChatRow(*row).last_message_ts
                if last_message_ts is None:
                    return None
                return last_message_ts if last_message_ts is datetime.datetime else datetime.datetime.fromisoformat(
                    last_message_ts)

    def add_all_messages(self, chat_id: int, messages: list[ChatMessage]):
        last_msg_dt = self._get_last_message_dt(chat_id)
        last_msg_id = -100
        added_users = set()
        with self._get_connection() as connection:
            cursor = connection.cursor()
            for message in messages:
                if (last_msg_dt is None) or (last_msg_dt < datetime.datetime.fromtimestamp(message.timestamp)):
                    last_msg_dt = datetime.datetime.fromtimestamp(message.timestamp)
                    last_msg_id = message.message_id
                if (message.user_id not in added_users) and (not self._user_exists(message.user_id)):
                    cursor.execute(self._QUERY_INSERT_INTO_USER,
                                   (message.user_id, False, 1))
                    cursor.execute(self._QUERY_INSERT_USER_INFO,
                                   (
                                       message.user_id,
                                       None,
                                       None,
                                       None,
                                       None,
                                       datetime.datetime.now()
                                   ))
                    user_info_id = cursor.fetchone()[0]
                    cursor.execute(self._QUERY_UPDATE_USER_LAST_ID, (user_info_id, message.user_id))
                    cursor.execute(self._QUERY_INSERT_INTO_USERS_CHATS,
                                   (message.user_id, chat_id, datetime.datetime.now(), 'user_chat_status'))
                    added_users.add(message.user_id)

                cursor.execute(self._QUERY_INSERT_INTO_CHAT_MESSAGES, (
                    message.message_id,
                    chat_id,
                    message.user_id,
                    datetime.datetime.fromtimestamp(message.timestamp),
                    message.content,
                    message.content_type,
                    message.frw_message_id
                ))
            if last_msg_id > 0:
                cursor.execute(
                    self._QUERY_UPDATE_CHAT_LAST_MESSAGE_INFO,
                    (last_msg_id, last_msg_dt, chat_id))
            connection.commit()

    def add_all_users(self, chat_id: int, users: list[UserRow]):
        with self._get_connection() as connection:
            cursor = connection.cursor()
            added_users = set()
            for user in users:
                if (user.user_id not in added_users) and (not self._user_exists(user.user_id)):
                    cursor.execute(self._QUERY_INSERT_INTO_USER,
                                   (user.user_id, user.is_bot, 1))
                    cursor.execute(self._QUERY_INSERT_USER_INFO,
                                   (
                                       user.user_id,
                                       user.username,
                                       user.first_name,
                                       user.last_name,
                                       user.phone,
                                       datetime.datetime.now()
                                   ))
                    user_info_id = cursor.fetchone()[0]
                    cursor.execute(self._QUERY_UPDATE_USER_LAST_ID, (user_info_id, user.user_id))
                    cursor.execute(self._QUERY_INSERT_INTO_USERS_CHATS,
                                   (user.user_id, chat_id, datetime.datetime.now(), 'user_chat_status'))
            connection.commit()

    def exist_chat(self, chat_id: int) -> bool:
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(self._QUERY_CHECK_CHAT_EXIST, (chat_id,))
            for row in cursor:
                return row[0]
            return False

    def _user_exists(self, user_id: int) -> bool:
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(self._QUERY_CHECK_USER_EXIST, (user_id,))
            for row in cursor:
                return row[0]
            return False

    def get_chats(self) -> list[ChatRow]:
        chats: list[ChatRow] = list()
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(self._QUERY_SELECT_ALL_CHATS)
            for row in cursor:
                chat_row = ChatRow(*row)
                chats.append(chat_row)
        return chats

    def get_chat(self, chat_id: int) -> ChatRow:
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(self._QUERY_SELECT_CHAT_BY_ID, (chat_id,))
            for row in cursor:
                return ChatRow(*row)

    def set_last_chat_check(self, chat_id: int):
        with self._get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(self._QUERY_SET_LAST_CHECK_IN_CHAT,
                           (datetime.datetime.now(), chat_id))


class CHTKDBPostgresImpl(PostgressConnection, BaseDB):
    def _queries_prepare(self) -> None:
        pass


class CHTKDBSQLiteImpl(SQLiteConnection, BaseDB):

    def _queries_prepare(self) -> None:
        self._QUERY_SELECT_LAST_MESSAGE_DATETIME = QUERY_SELECT_LAST_MESSAGE_DATETIME.replace("%s", "?")
        self._QUERY_INSERT_INTO_USER = QUERY_INSERT_INTO_USER.replace("%s", "?")
        self._QUERY_INSERT_USER_INFO = QUERY_INSERT_USER_INFO.replace("%s", "?")
        self._QUERY_INSERT_INTO_USERS_CHATS = QUERY_INSERT_INTO_USERS_CHATS.replace("%s", "?")
        self._QUERY_INSERT_INTO_CHAT_MESSAGES = QUERY_INSERT_INTO_CHAT_MESSAGES.replace("%s", "?")
        self._QUERY_UPDATE_CHAT_LAST_MESSAGE_INFO = QUERY_UPDATE_CHAT_LAST_MESSAGE_INFO.replace("%s", "?")
        self._QUERY_CHECK_USER_EXIST = QUERY_CHECK_USER_EXIST.replace("%s", "?")
        self._QUERY_CHECK_CHAT_EXIST = QUERY_CHECK_CHAT_EXIST.replace("%s", "?")
        self._QUERY_SELECT_ALL_CHATS = QUERY_SELECT_ALL_CHATS.replace("%s", "?")
        self._QUERY_SELECT_CHAT_BY_ID = QUERY_SELECT_CHAT_BY_ID.replace("%s", "?")
        self._QUERY_SET_LAST_CHECK_IN_CHAT = QUERY_SET_LAST_CHECK_IN_CHAT.replace("%s", "?")
        self._QUERY_UPDATE_USER_LAST_ID = QUERY_UPDATE_USER_LAST_ID.replace("%s", "?")
