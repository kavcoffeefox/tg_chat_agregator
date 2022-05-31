drop table users_chats;
drop table chat_messages;
drop table user_info;
drop table users;
drop table chats;


CREATE TABLE chats (
  chat_id bigint NOT NULL,
  chat_n_subscribers integer NOT NULL,
  chat_n_messages integer NOT NULL,
  last_message_id integer DEFAULT NULL,
  last_message_ts timestamp DEFAULT NULL,
  last_info_id integer NOT NULL,
  date_last_update timestamp NOT NULL,
  CONSTRAINT chats_pkey PRIMARY KEY (chat_id)
);

CREATE TABLE users (
  user_id bigint NOT NULL,
  is_bot bool,
  last_info_id integer,
  CONSTRAINT users_pkey PRIMARY KEY (user_id)
);

CREATE TABLE user_info (
  info_id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  user_id bigint NOT NULL,
  username varchar(32) DEFAULT NULL,
  first_name varchar(32) DEFAULT NULL,
  last_name varchar(32) DEFAULT NULL,
  phone char(10) DEFAULT NULL,
  update_date timestamp NOT NULL,
  CONSTRAINT user_info_user_id_users_user_id_foreign FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE chat_info (
  info_id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  chat_id bigint NOT NULL,
  chat_link varchar(32) NOT NULL,
  username varchar(32) DEFAULT NULL,
  title varchar(32) NOT NULL,
  description text NOT NULL,
  update_date timestamp NOT NULL,
  CONSTRAINT chat_info_chat_id_chats_chat_id_foreign FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
);

CREATE TABLE chat_messages (
  message_id integer NOT NULL,
  chat_id bigint NOT NULL,
  user_id bigint NOT NULL,
  timestamp timestamp NOT NULL,
  content text NOT NULL,
  content_type integer NOT NULL,
  frw_message_id integer DEFAULT NULL,
  CONSTRAINT chat_messages_pkey PRIMARY KEY (message_id),
  CONSTRAINT chat_messages_chat_id_chats_chat_id_foreign FOREIGN KEY (chat_id) REFERENCES chats (chat_id),
  CONSTRAINT chat_messages_user_id_users_user_id_foreign FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE users_chats (
  id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  user_id bigint NOT NULL,
  chat_id bigint NOT NULL,
  joining_date timestamp NOT NULL,
  user_chat_status varchar(16) NOT NULL,
  CONSTRAINT users_chats_chat_id_chats_chat_id_foreign FOREIGN KEY (chat_id) REFERENCES chats (chat_id),
  CONSTRAINT users_chats_user_id_users_user_id_foreign FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- test examples
INSERT INTO chats(chat_id, chat_n_subscribers, chat_n_messages, last_info_id, date_last_update)
VALUES (100, 0, 0, 100, current_timestamp);
INSERT INTO chats(chat_id, chat_n_subscribers, chat_n_messages, last_info_id, date_last_update)
VALUES (200, 0, 0, 100, current_timestamp);
INSERT INTO chats(chat_id, chat_n_subscribers, chat_n_messages, last_info_id, date_last_update)
VALUES (300, 0, 0, 100, current_timestamp);
INSERT INTO chats(chat_id, chat_n_subscribers, chat_n_messages, last_info_id, date_last_update)
VALUES (400, 0, 0, 100, current_timestamp);
INSERT INTO chats(chat_id, chat_n_subscribers, chat_n_messages, last_info_id, date_last_update)
VALUES (500, 0, 0, 100, current_timestamp);
