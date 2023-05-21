import re
from flask import Blueprint, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.member import Member


# Create the marshmallow schema

class MemberSchema(schema.Schema):
    class Meta:
        model = Member
        fields = ("id", "name", "email", "phone_number", "address", "outstanding_debt")


# Create the blueprint

member = Blueprint("member", __name__)

# Create the marshmallow instance

member_schema = MemberSchema()

# Create the routes

@member.route("/members", methods=["GET"])
def get_members():
    members = Member.query.all()
    return jsonify(member_schema.dump(members,many=True))

@member.route("/members/<int:id>", methods=["GET"])
def get_member(id):
    member = Member.query.get(id)
    return jsonify(member_schema.dump(member))

@member.route("/members", methods=["POST"])
def create_member():
    data = request.json
    # Validate the data
    if not data["name"]:
        return jsonify({"message": "Name is required"})
    if not data["email"]:
        return jsonify({"message": "Email is required"})
    if not data["phone_number"]:
        return jsonify({"message": "Phone number is required"})
    if not data["address"]:
        return jsonify({"message": "Address is required"})

    # Validate the email
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}$', data["email"]):
        return jsonify({"message": "Invalid email address"})
    # Validate the phone number
    if not re.match(r"^(?:\+?1)?[-.\s]?\(?\d{3}?\)?[-.\s]?\d{3}[-.\s]?\d{4}$", data["phone_number"]):
        return jsonify({"message": "Invalid phone number"})

    member = Member(name=data["name"], email=data["email"], phone_number=data["phone_number"], address=data["address"])
    db.session.add(member)
    db.session.commit()
    return jsonify(member_schema.dump(member))

@member.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    data = request.json
    # Validate the data
    if not data["name"]:
        return jsonify({"message": "Name is required"})
    if not data["email"]:
        return jsonify({"message": "Email is required"})
    if not data["phone_number"]:
        return jsonify({"message": "Phone number is required"})
    if not data["address"]:
        return jsonify({"message": "Address is required"})

    # Validate the email
    if not re.match(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]', data["email"]):
        return jsonify({"message": "Invalid email address"})
    # Validate the phone number
    if not re.match(r"^\[0\-9\]\{10\}", data["phone_number"]):
            return jsonify({"message": "Invalid phone number"})