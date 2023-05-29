import re
from flask import Blueprint, jsonify, request, render_template
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
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    members = Member.query.paginate(page=page, per_page=per_page)
    total_pages = members.pages

    return render_template('members.html', members=members, total_pages=total_pages)

@member.route("/add-member", methods=["GET"])
def get_add_member():
    return render_template("add-member.html", is_edit=False)

@member.route("/members/<int:id>", methods=["GET"])
def get_member(id):
    member = Member.query.get(id)
    return jsonify(member_schema.dump(member))

@member.route("/edit-member/<int:member_id>", methods=["GET"])
def get_edit_member(member_id):
    member = Member.query.get_or_404(member_id)
    return render_template("add-member.html", is_edit=True, member=member)

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

    member = Member(name=data["name"], email=data["email"], phone_number=data["phone_number"], address=data["address"], outstanding_debt=data["outstanding_debt"])
    db.session.add(member)
    db.session.commit()
    return jsonify(member_schema.dump(member))

@member.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({"message": "Member not found"})

    data = request.json
    # Validate the data
    if not data.get("name"):
        return jsonify({"message": "Name is required"})
    if not data.get("email"):
        return jsonify({"message": "Email is required"})
    if not data.get("phone_number"):
        return jsonify({"message": "Phone number is required"})
    if not data.get("address"):
        return jsonify({"message": "Address is required"})

# Validate the email
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}$', data["email"]):
        return jsonify({"message": "Invalid email address"})
    # Validate the phone number
    if not re.match(r"^(?:\+?1)?[-.\s]?\(?\d{3}?\)?[-.\s]?\d{3}[-.\s]?\d{4}$", data["phone_number"]):
        return jsonify({"message": "Invalid phone number"})

    # Update the member data
    member.name = data["name"]
    member.email = data["email"]
    member.phone_number = data["phone_number"]
    member.address = data["address"]
    member.outstanding_debt = data.get("outstanding_debt", 0)

    db.session.commit()

    return jsonify({"message": "Member updated successfully"})     

@member.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({"message": "Member not found"})

    db.session.delete(member)
    db.session.commit()

    return jsonify({"message": "Member deleted successfully"})
