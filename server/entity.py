from collections import namedtuple

ChatRow = namedtuple("ChatRow",
                     ["chat_id", "chat_link", "chat_n_subscribers", "chat_n_messages", "last_message_id",
                      "last_message_ts", "last_info_id", "date_last_update"])

UserRow = namedtuple("UserRow",
                     "user_id is_bot username first_name last_name phone")

ChatMessage = namedtuple("ChatMessage",
                         "message_id chat_id user_id timestamp content content_type frw_message_id")


