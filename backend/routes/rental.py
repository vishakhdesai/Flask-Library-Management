from flask import Blueprint, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.rental import Rental


# Create the marshmallow schema

class RentalSchema(schema.Schema):
    class Meta:
        model = Rental
        fields = ("id", "book_id", "member_id", "start_date", "end_date", "rent_fee")


# Create the blueprint

rental = Blueprint("rental", __name__)

# Create the marshmallow instance

rental_schema = RentalSchema()

# Create the routes

@rental.route("/rentals", methods=["GET"])
def get_rentals():
    rentals = Rental.query.all()
    return jsonify(rental_schema.dump(rentals, many=True))

@rental.route("/rentals/<int:id>", methods=["GET"])
def get_rental(id):
    rental = Rental.query.get(id)
    return jsonify(rental_schema.dump(rental))

@rental.route("/rentals", methods=["POST"])
def create_rental():
    data = request.json
    # Validate the data
    if not data["book_id"]:
        return jsonify({"message": "Book ID is required"})
    if not data["member_id"]:
        return jsonify({"message": "Member ID is required"})
    if not data["start_date"]:
        return jsonify({"message": "Start date is required"})
    if not data["end_date"]:
        return jsonify({"message": "End date is required"})

    rental = Rental(book_id=data["book_id"], member_id=data["member_id"], start_date=data["start_date"], end_date=data["end_date"])
    db.session.add(rental)
    db.session.commit()
    return jsonify(rental_schema.dump(rental))

@rental.route("/rentals/<int:id>", methods=["PUT"])
def update_rental(id):
    data = request.json
    # Validate the data
    if not data["book_id"]:
        return jsonify({"message": "Book ID is required"})
    if not data["member_id"]:
        return jsonify({"message": "Member ID is required"})
    if not data["start_date"]:
        return jsonify({"message": "Start date is required"})
    if not data["end_date"]:
        return jsonify({"message": "End date is required"})

    rental = Rental.query.get(id)
    rental.book_id = data["book_id"]
    rental.member_id = data["member_id"]
    rental.start_date = data["start_date"]
    rental.end_date = data["end_date"]
    db.session.commit()
    return jsonify(rental_schema.dump(rental))

@rental.route("/rentals/<int:id>", methods=["DELETE"])
def delete_rental(id):
    rental = Rental.query.get(id)
    db.session.delete(rental)
    db.session.commit()
    return jsonify({"message": "Rental deleted"})
