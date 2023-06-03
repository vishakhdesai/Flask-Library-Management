from ..extensions import db

class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(100))
    address = db.Column(db.String(100))
    outstanding_debt = db.Column(db.Integer)
    issue_list = db.Column(db.String(255))
    books_issue_limit = db.Column(db.Integer)