# -*- coding: utf-8 -*-
# !/usr/bin/python3
import flask
from flask import request, jsonify
from settings import BASE_URL_PART, DATABASE_TYPE

from managers import Manager, InputJSONNotValid, JobNotValid

app = flask.Flask(__name__)

expected_json = {
    "users": """[{
		"id": 1482791582, // id чата в который добавляются пользователи
		"users": [
			{
				"username": "Name1",
				"userid": 123456780,
				"first_name": "123",
				"second_name": null,
				"phone": null,
				"is_bot": false
			},
			{
				"username": "Name2",
				"userid": 123456781,
				"first_name": "4456",
				"second_name": "You",
				"phone": 999999999,
				"is_bot": true
			}]
	}]""", }

chtk_manager = Manager(DATABASE_TYPE)


@app.route(BASE_URL_PART + "/add_user", methods=["POST"])
@app.route(BASE_URL_PART + "/add_users", methods=["POST"])
def add_users():
    json = request.get_json()
    payload = json[0]
    try:
        chtk_manager.add_users(payload['id'], payload["users"])
        return jsonify({"status": True, "Message": "Success"})
    except InputJSONNotValid:
        return jsonify({"status": False, "message": "Input invalid", "expected": expected_json["users"]})


@app.route(BASE_URL_PART + '/add_message', methods=["POST"])
@app.route(BASE_URL_PART + '/add_messages', methods=["POST"])
def add_messages():
    json = request.get_json()
    payload = json[0]
    try:
        chtk_manager.add_messages(chat_id=payload['id'], messages=payload["messages"])
        chtk_manager.complete_job(payload.get("job_id", " "), payload['id'])
        return jsonify({"status": True, "Message": "Success"})
    except JobNotValid:
        return jsonify({"status": False, "message": "Job not valid or timeout"})
    except InputJSONNotValid:
        return jsonify({"status": False, "message": "Input invalid", "expected": expected_json["users"]})


@app.route(BASE_URL_PART + '/get_job', methods=['GET'])
def get_job():
    return jsonify(chtk_manager.get_job())


@app.route(BASE_URL_PART + '/add_session', methods=["POST"])
@app.route(BASE_URL_PART + '/add_sessions', methods=["POST"])
def add_sessions():
    json = request.get_json()
    chtk_manager.add_sessions(json)
    return jsonify({"status": True, "Message": "Success"})


if __name__ == '__main__':
    app.run(debug=True)
