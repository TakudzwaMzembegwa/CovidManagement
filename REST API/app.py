from email import message
import string
from flask import Flask, request, jsonify
from datetime import datetime
import db
import schema
app = Flask(__name__)


@app.route("/user", methods=['POST'])
def user():
    # Updates a user if they exist, else it creates a new user
    student_no = request.form.get('studentNumber')
    mask = request.form.get('mask')
    desk = request.form.get('desk')
    db.user_db.update_one({"_id": int(student_no)},
                          {"$inc": {"accessCounter": 1}, "$set": {"_id": int(student_no), "mask": mask, "desk": desk, "date": datetime.now().replace(microsecond=0)}}, upsert=True)
    return jsonify(message="Ok")


@ app.route("/users")
def users():
    # Gets users with a building from the DB
    f = db.user_db.find({'desk': {'$ne': ''}})
    data = [user for user in f]
    return jsonify(schema.users_serializer(data))


@ app.route("/useratdesk/<string:desk>")
def users(desk: string):
    # Gets users with a building from the DB
    f = db.user_db.find({'desk': {'$eq': desk}})
    data = [user for user in f]
    return jsonify(schema.users_serializer(data))


@ app.route("/building/<string:name>")
def seats(name: string):
    # Gets a seat from the DB by name
    data = db.building_db.find({"_id": name})[0]
    return jsonify(schema.building_serializer(data))


@ app.route("/building", methods=['POST'])
def seat_state():
    """
    Method to update desk state
    Receives new data from a form
    Returns desks before update
    """
    building = request.form.get('building')
    desk = request.form.get('desk')
    state = request.form.get('state')
    data = db.building_db.find({"_id": building})[0]
    data['desks'][desk] = state
    print(data['_id'])
    db.building_db.update_one({"_id": data['_id']},
                              {"$set": {"desks": data['desks'], "date": datetime.now().replace(microsecond=0)}})
    return jsonify(schema.building_serializer(data))


@ app.route("/user/<int:id>")
def get_user(id: int):
    # Gets an existing user from the DB
    data = db.user_db.find({"_id": int(id)})[0]
    return jsonify(schema.user_serializer(data))


if __name__ == '__main__':
    app.run(debug=True)
