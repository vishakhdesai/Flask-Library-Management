import requests
import ast
import json
from urllib.parse import urlencode
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template, redirect, request
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.book import Book


class BookSchema(schema.Schema):
    class Meta:
        model = Book
        fields = (
            "id", "bookID", "title", "authors", "average_rating", "isbn", "isbn13",
            "language_code", "num_pages", "ratings_count", "text_reviews_count",
            "publication_date", "publisher", "quantity"
        )

book = Blueprint("book", __name__)

book_schema = BookSchema()

def validate_book(book:dict):
    labels = {
        "title": "Title",
        "authors":"Authors",
        "language_code": "Language Code",
        "num_pages": "Number of pages",
        "publisher": "Publisher",
        "quantity": "Quantity",
        "publication_date": "Publication Date",
    }
    fields = ["title","authors","language_code","num_pages","publisher","quantity","publication_date"]
    required = []
    for field in fields:
        if not book.get(field):
            required.append(labels[field])

    if len(required) > 0:
        msg = ",".join(required)
        msg = f"Field(s): {msg} is/are required!"
        return False, msg
    else:
        return True, ""

@book.route('/import-books', methods=["GET"])
def import_books():
    try:
        title = request.args.get("title", "")
        authors = request.args.get("authors", "")
        page = request.args.get("page", 1)
        
        # Make a request to the API.
        params = {
            'title': title,
            'authors': authors,
            'page': page
        }
        encoded_params = urlencode(params)
        response = requests.get(
            "https://frappe.io/api/method/frappe-library?{}".format(
                encoded_params
            )
        )

        if response.status_code != 200:
            return jsonify({"message": "Error fetching books from API"}), 500

        books = response.json()["message"]
        existing_book_ids = [book.bookID for book in Book.query.all()] 
        
        for book in books:
            if book['bookID'] in existing_book_ids:
                book['exists_in_database'] = True 
            else:
                book['exists_in_database'] = False

        return render_template("import-books.html", books=books, title=title, authors=authors), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/books", methods=["GET"])
def get_books():
    try:
        page = int(request.args.get("page", 1))
        title = request.args.get("title")
        authors = request.args.get("authors")
        per_page = int(request.args.get("per_page", 20))

        if title and authors:
            books = Book.query.filter(Book.title.contains(title) & Book.authors.contains(authors)).paginate(page=page, per_page=per_page)
        elif title:
            books = Book.query.filter(Book.title.contains(title)).paginate(page=page, per_page=per_page)
        elif authors:
            books = Book.query.filter(Book.authors.contains(authors)).paginate(page=page, per_page=per_page)
        else:
            books = Book.query.order_by(Book.id).paginate(page=page, per_page=per_page)
            
        total_pages = books.pages
        books = book_schema.dump(books.items, many=True)
        title = request.args.get("title", "")
        authors = request.args.get("authors", "")
        return render_template("library-books.html", books=books, title=title, authors=authors, total_pages=total_pages), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/books/<int:id>", methods=["GET"])
def get_book(id):
    try:
        book = Book.query.get(id)
        if not book:
            return render_template("404.html"), 404

        return render_template("book.html", book=book)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/import-books", methods=["POST"])
def create_books():
    try:
        data = request.json
        data = [ast.literal_eval(item) for item in data]
        
        if not data:
            return jsonify({"message": "No data was provided"}), 400
        
        for book in data:
            publication_date = datetime.strptime(book["publication_date"], "%m/%d/%Y").strftime("%Y-%m-%d")
            average_rating = float(book["average_rating"])
            ratings_count = int(book["ratings_count"])
            text_reviews_count = int(book["text_reviews_count"])
            
            book = Book(
                bookID=book["bookID"],
                title=book["title"], 
                authors=book["authors"], 
                isbn=book["isbn"], 
                average_rating=average_rating,
                text_reviews_count=text_reviews_count,
                ratings_count=ratings_count,
                isbn13=book["isbn13"], 
                language_code=book["language_code"], 
                num_pages=book["  num_pages"], 
                publication_date=publication_date, 
                publisher=book["publisher"],
                quantity=0
            )
            
            db.session.add(book)

        db.session.commit()
        return jsonify({"message": "Books created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/books/<int:id>", methods=["PUT"])
def update_book(id):
    try:
        book_data = request.json
        data = json.loads(book_data["book"])
        valid, msg = validate_book(data)
        if not valid:
            return jsonify({"message": msg}), 400
        data["quantity"] = book_data["quantity"]

        book = Book.query.get(id)
        if not book:
            return render_template("404.html"), 404

        book.title = data["title"]
        book.authors = data["authors"]
        book.language_code = data["language_code"]
        book.num_pages = data["num_pages"]
        book.publisher = data["publisher"]
        book.quantity = int(data["quantity"])
        book.publication_date = data["publication_date"]
        
        db.session.commit()
        return jsonify(book_schema.dump(book)), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/edit-book/<int:id>", methods=["GET"])
def get_edit_book(id):
    try:
        book = Book.query.get(id)
        if not book:
            return render_template("404.html"), 404

        return render_template("edit-book.html", book=book), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/books/<int:id>", methods=["DELETE"])
def delete_book(id):
    try:
        book = Book.query.get(id)
        if not book:
            return render_template("404.html"), 404

        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
