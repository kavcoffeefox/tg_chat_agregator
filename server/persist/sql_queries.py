QUERY_INSERT_INTO_USER = "INSERT INTO users(user_id, is_bot, last_info_id) VALUES (%s, %s, %s)"
QUERY_UPDATE_USER_LAST_ID = "UPDATE users SET last_info_id = %s WHERE user_id=%s"
QUERY_INSERT_USER_INFO = "INSERT INTO user_info" \
                         "(user_id, username, first_name, last_name, phone, update_date) " \
                         "VALUES (%s, %s, %s, %s, %s, %s) RETURNING info_id"
QUERY_INSERT_INTO_USERS_CHATS = "INSERT INTO users_chats(user_id, chat_id, joining_date, user_chat_status) " \
                                "VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"

QUERY_SELECT_LAST_MESSAGE_DATETIME = "SELECT * FROM chats WHERE chat_id=%s"

QUERY_INSERT_INTO_CHAT_MESSAGES = "INSERT INTO chat_messages(message_id, chat_id, " \
                                  "user_id, timestamp, content, content_type, frw_message_id)" \
                                  "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
QUERY_UPDATE_CHAT_LAST_MESSAGE_INFO = "update chats set (last_message_id, last_message_ts) = (%s, %s) where chat_id=%s"
QUERY_CHECK_USER_EXIST = "select exists(select 1 from users where user_id=%s)"

QUERY_SELECT_ALL_CHATS = "select c.chat_id, ci.chat_link, c.chat_n_subscribers, c.chat_n_messages, " \
                         "c.last_message_id, c.last_message_ts, c.last_info_id, c.date_last_update from chats as c " \
                         "INNER JOIN  chat_info as ci ON ci.chat_id = c.chat_id"
QUERY_CHECK_CHAT_EXIST = "select exists(select 1 from chats where chat_id=%s)"
QUERY_SELECT_CHAT_BY_ID = "select * from chats where chat_id=%s"
QUERY_SET_LAST_CHECK_IN_CHAT = "update chats set date_last_update = (%s) where chat_id=%s"