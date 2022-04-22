from email import message
from flask import Flask, request, jsonify
from datetime import datetime
import db
import schema
app = Flask(__name__)


@app.route("/user", methods=['POST'])
def user():
    student_no = request.form.get('studentNumber')
    mask = request.form.get('mask')
    pc = request.form.get('pc')
    db.facemask.update_one({"_id": int(student_no)},
                           {"$setOnInsert": {"_id": int(student_no), "mask": mask, "pc": pc, "date": datetime.now().replace(microsecond=0)}}, upsert=True)
    return jsonify(message="Connected to the data base!")


@ app.route("/users")
def users():
    f = db.facemask.find()
    data = [user for user in f]
    return jsonify(schema.users_serializer(data))


@ app.route("/user/<int:id>")
def get_user(id: int):
    data = db.facemask.find({"_id": int(id)})[0]
    return jsonify(schema.user_serializer(data))


if __name__ == '__main__':
    app.run(debug=True)
