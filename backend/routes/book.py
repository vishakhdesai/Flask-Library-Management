import requests
import ast
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template, redirect, request
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.book import Book


# Create the marshmallow schema

class BookSchema(schema.Schema):
    class Meta:
        model = Book
        fields = (
            "id", "bookID", "title", "authors", "average_rating", "isbn", "isbn13",
            "language_code", "num_pages", "ratings_count", "text_reviews_count",
            "publication_date", "publisher", "quantity"
        )


# Create the blueprint

book = Blueprint("book", __name__)

# Create the marshmallow instance

book_schema = BookSchema()

# Create the routes

@book.route('/import-books', methods=["GET"])
def import_books():
    try:
        title = request.args.get("title", "")
        authors = request.args.get("authors", "")
        page = request.args.get("page", 1)
        
        # Make a request to the API.
        title_req = "&title=" + title
        authors_req = "&authors=" + authors
        response = requests.get(
            "https://frappe.io/api/method/frappe-library?page={}{}{}".format(
                page, title_req, authors_req
            )
        )

        # Check the response status code.
        if response.status_code != 200:
            return jsonify({"message": "Error fetching books from API"}), 500

        # Get the books from the response.
        books = response.json()
        books = books["message"]
        existing_book_ids = [book.bookID for book in Book.query.all()] 
        
        for book in books:
            if book['bookID'] in existing_book_ids:
                book['exists_in_database'] = True  # Add a field to indicate if the book exists in the database
            else:
                book['exists_in_database'] = False

        # Render the template with the books.
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
            books = Book.query.paginate(page=page, per_page=per_page)
            
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
            return jsonify({"message": "Book not found"}), 404

        return jsonify(book_schema.dump(book)), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/import-books", methods=["POST"])
def create_books():
    try:
        data = request.json
        data = [ast.literal_eval(item) for item in data]
        
        # Validate the data
        if not data:
            return jsonify({"message": "No data was provided"}), 400
        
        for book in data:
            if not book["bookID"]:
                return jsonify({"message": "bookID is required"}), 400
            if not book["title"]:
                return jsonify({"message": "Title is required"}), 400
            if not book["authors"]:
                return jsonify({"message": "Authors is required"}), 400
            if not book["isbn"]:
                return jsonify({"message": "ISBN is required"}), 400
            if not book["isbn13"]:
                return jsonify({"message": "ISBN13 is required"}), 400
            if not book["language_code"]:
                return jsonify({"message": "Language code is required"}), 400
            if not book["  num_pages"]:
                return jsonify({"message": "Number of pages is required"}), 400
            if not book["publication_date"]:
                return jsonify({"message": "Publication date is required"}), 400
            if not book["publisher"]:
                return jsonify({"message": "Publisher is required"}), 400

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
        data = ast.literal_eval(book_data["book"])
        data["quantity"] = book_data["quantity"]

        book = Book.query.get(id)
        if not book:
            return jsonify({"message": "Book not found"}), 404

        book.title = data["title"]
        book.authors = data["authors"]
        book.language_code = data["language_code"]
        book.num_pages = data["num_pages"]
        book.publisher = data["publisher"]
        book.quantity = int(data["quantity"])
        book.publication_date = data["publication_date"]
        book.average_rating = float(data["average_rating"])
        book.ratings_count = int(data["ratings_count"])
        book.text_reviews_count = int(data["text_reviews_count"])
        
        db.session.commit()
        return jsonify(book_schema.dump(book)), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/edit-book/<int:id>", methods=["GET"])
def get_edit_book(id):
    try:
        book = Book.query.get(id)
        if not book:
            return jsonify({"message": "Book not found"}), 404

        return render_template("edit-book.html", book=book), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@book.route("/books/<int:id>", methods=["DELETE"])
def delete_book(id):
    try:
        book = Book.query.get(id)
        if not book:
            return jsonify({"message": "Book not found"}), 404

        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Book deleted"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
