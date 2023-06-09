import re
from flask import Blueprint, jsonify, request, render_template
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.member import Member
from ..models.rental import Rental

class MemberSchema(schema.Schema):
    class Meta:
        model = Member
        fields = ("id", "name", "email", "phone_number", "address", "outstanding_debt")

member = Blueprint("member", __name__)

member_schema = MemberSchema()

def validate_member(member_details:dict):
    labels = {"name": "Name", "email": "Email", "phone_number":"Phone Number"}
    fields = ["name", "email"]
    required = []
    invalid = []
    for field in fields:
        if not member_details.get(field):
            required.append(labels[field])
            continue
    if required:
        msg = ",".join(required)
        msg = f"Field(s): {msg} is/are required!"
        return False, msg
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', member_details.get("email")):
        invalid.append(labels["email"])
    if member_details.get("phone_number"):
        if not re.match(r"^(?:\+?1)?[-.\s]?\(?\d{3}?\)?[-.\s]?\d{3}[-.\s]?\d{4}$", member_details.get("phone_number")):
            invalid.append(labels["phone_number"])
    if len(invalid) > 0:
        msg = ",".join(invalid)
        msg = f"Field(s): {msg} is/are invalid!"
        return False, msg
    else:
        return True, ""
        
    
@member.route("/members", methods=["GET"])
def get_members():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        name = request.args.get('name')
        email = request.args.get('email')
        if name and email:
            members = Member.query.filter(Member.name.contains(name) & Member.email.contains(email)).paginate(page=page, per_page=per_page) 
        elif name:
            members = Member.query.filter(Member.name.contains(name)).paginate(page=page, per_page=per_page)
        elif email:
            members = Member.query.filter(Member.email.contains(email)).paginate(page=page, per_page=per_page)
        else:
            members = Member.query.order_by(Member.id).paginate(page=page, per_page=per_page)
        total_pages = members.pages
        name = request.args.get('name', '')
        email = request.args.get('email', '')
        return render_template('members.html', members=members, total_pages=total_pages, name=name, email=email), 200
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
            return render_template("404.html"), 404
        return render_template("member.html", member=member), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@member.route("/edit-member/<int:member_id>", methods=["GET"])
def get_edit_member(member_id):
    try:
        member = Member.query.get(member_id)
        return render_template("add-member.html", is_edit=True, member=member), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@member.route("/members", methods=["POST"])
def create_member():
    try:
        data = request.json
        valid, msg = validate_member(data)
        if not valid:
            return jsonify({"message": msg}), 400

        member = Member(name=data["name"], email=data["email"], phone_number=data["phone_number"], address=data["address"], outstanding_debt=data["outstanding_debt"], books_issue_limit=5)
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
            return render_template("404.html"), 404

        data = request.json
        valid, msg = validate_member(data)
        if not valid:
            return jsonify({"message": msg}), 400

        member.name = data["name"]
        member.email = data["email"]
        member.phone_number = data["phone_number"]
        member.address = data["address"]
        member.outstanding_debt = data.get("outstanding_debt", 0)
        db.session.commit()

        return jsonify({"message": "Member updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@member.route("/make-payment/<int:rentalId>", methods=["POST"])
def make_payment(rentalId):
    try:
        rental = Rental.query.get(rentalId)
        member = Member.query.get(rental.member_id)
        payment = int(request.json["payment"])
        if rental.payment:
            rental.payment += payment
        else:
            rental.payment = payment
        member.outstanding_debt -= payment
        db.session.commit()
        return jsonify({"message": "Payment Success"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
        

@member.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        member = Member.query.get(id)
        rentals = Rental.query.filter(Rental.member_id==member.id, Rental.book_returned==False).all()
        if not member:
            return render_template("404.html"), 404
        if len(rentals) > 0:
            return jsonify({"message": "Cannot delete member as the member have issued books"}), 400
        db.session.delete(member)
        db.session.commit()

        return jsonify({"message": "Member deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
