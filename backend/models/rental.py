from ..extensions import db

class Rental(db.Model):
    __tablename__ = "rentals"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    rent_fee = db.Column(db.Integer)

    member = db.relationship("Member", backref="members")
    book = db.relationship("Book", backref="rentals")