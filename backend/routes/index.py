from flask import Blueprint, jsonify, request, render_template, request, redirect, url_for, flash
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.book import Book
from ..models.member import Member
from ..models.rental import Rental, BookRental

index = Blueprint("index", __name__)

@index.route("/", methods = ["GET"])
def home():
    
    top_rented_books = Book.query.join(BookRental).group_by(Book.id).order_by(db.func.count(BookRental.id).desc()).all()
    
    for book in top_rented_books:
        book.issued_times = len(book.book_rentals)
    top_debt_members = Member.query.order_by(Member.outstanding_debt.desc()).limit(10).all()

    top_rated_books = Book.query.order_by(Book.average_rating.desc()).limit(10).all()

    top_renting_members = Member.query.join(Rental).group_by(Member.id).order_by(db.func.count(Rental.id).desc()).limit(10).all()

    return render_template('index.html', top_rented_books=top_rented_books,
                           top_debt_members=top_debt_members, top_rated_books=top_rated_books,
                           top_renting_members=top_renting_members)