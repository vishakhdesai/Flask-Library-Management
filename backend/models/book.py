from ..extensions import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bookID = db.Column(db.String(255))
    title = db.Column(db.String(255))
    authors = db.Column(db.String(255))
    average_rating = db.Column(db.Float)
    isbn = db.Column(db.String(13))
    isbn13 = db.Column(db.String(13))
    language_code = db.Column(db.String(255))
    num_pages = db.Column(db.Integer)
    ratings_count = db.Column(db.Integer)
    text_reviews_count = db.Column(db.Integer)
    publication_date = db.Column(db.Date)
    publisher = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
