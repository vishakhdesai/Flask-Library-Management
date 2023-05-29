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
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        members = Member.query.paginate(page=page, per_page=per_page)
        total_pages = members.pages
        return render_template('members.html', members=members, total_pages=total_pages), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@member.route("/add-member", methods=["GET"])
def get_add_member():
    return render_template("add-member.html", is_edit=False), 200

@member.route("/members/<int:id>", methods=["GET"])
def get_member(id):
    try:
        member = Member.query.get(id)
        if not member:
            return jsonify({"message": "Member not found"}), 404
        return jsonify(member_schema.dump(member)), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@member.route("/edit-member/<int:member_id>", methods=["GET"])
def get_edit_member(member_id):
    try:
        member = Member.query.get_or_404(member_id)
        return render_template("add-member.html", is_edit=True, member=member), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@member.route("/members", methods=["POST"])
def create_member():
    try:
        data = request.json
        if not data.get("name"):
            return jsonify({"message": "Name is required"}), 400
        if not data.get("email"):
            return jsonify({"message": "Email is required"}), 400
        if not data.get("phone_number"):
            return jsonify({"message": "Phone number is required"}), 400
        if not data.get("address"):
            return jsonify({"message": "Address is required"}), 400

        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}$', data["email"]):
            return jsonify({"message": "Invalid email address"}), 400

        if not re.match(r"^(?:\+?1)?[-.\s]?\(?\d{3}?\)?[-.\s]?\d{3}[-.\s]?\d{4}$", data["phone_number"]):
            return jsonify({"message": "Invalid phone number"}), 400

        member = Member(name=data["name"], email=data["email"], phone_number=data["phone_number"], address=data["address"], outstanding_debt=data["outstanding_debt"])
        db.session.add(member)
        db.session.commit()

        return jsonify(member_schema.dump(member)), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@member.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member = Member.query.get(id)
        if not member:
            return jsonify({"message": "Member not found"}), 404

        data = request.json
        if not data.get("name"):
            return jsonify({"message": "Name is required"}), 400
        if not data.get("email"):
            return jsonify({"message": "Email is required"}), 400
        if not data.get("phone_number"):
            return jsonify({"message": "Phone number is required"}), 400
        if not data.get("address"):
            return jsonify({"message": "Address is required"}), 400

        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}$', data["email"]):
            return jsonify({"message": "Invalid email address"}), 400

        if not re.match(r"^(?:\+?1)?[-.\s]?\(?\d{3}?\)?[-.\s]?\d{3}[-.\s]?\d{4}$", data["phone_number"]):
            return jsonify({"message": "Invalid phone number"}), 400

        member.name = data["name"]
        member.email = data["email"]
        member.phone_number = data["phone_number"]
        member.address = data["address"]
        member.outstanding_debt = data.get("outstanding_debt", 0)
        db.session.commit()

        return jsonify({"message": "Member updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@member.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        member = Member.query.get(id)
        if not member:
            return jsonify({"message": "Member not found"}), 404

        db.session.delete(member)
        db.session.commit()

        return jsonify({"message": "Member deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
