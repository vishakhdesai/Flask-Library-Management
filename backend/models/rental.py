from ..extensions import db

class Rental(db.Model):
    __tablename__ = "rentals"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    total_rent_fee = db.Column(db.Integer)
    book_returned = db.Column(db.Boolean)
    payment = db.Column(db.Integer)
    
    member = db.relationship("Member", backref="rentals")
    
class BookRental(db.Model):
    __tablename__ = "book_rentals"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    rental_id = db.Column(db.Integer, db.ForeignKey("rentals.id"))
    rent_fee = db.Column(db.Integer)

    book = db.relationship("Book", backref="book_rentals")
    rental = db.relationship("Rental", backref="book_rentals")