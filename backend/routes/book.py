from flask import Blueprint, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.book import Book, BookStock


# Create the marshmallow schema

class BookSchema(schema.Schema):
    class Meta:
        model = Book
        fields = ("id", "bookID", "title", "authors", "average_rating", "isbn", "isbn13", "language_code", "num_pages", "ratings_count", "text_reviews_count", "publication_date", "publisher")


# Create the blueprint

book = Blueprint("book", __name__)

# Create the marshmallow instance

book_schema = BookSchema()

# Create the routes

@book.route("/books", methods=["GET"])
def search_books():
    page = request.args.get("page", 1)
    title = request.args.get("title")
    author = request.args.get("author")
    per_page = 20

    if title and author:
        books = Book.query.filter(Book.title.contains(title) & Book.authors.contains(author)).paginate(page=page, per_page=per_page)
    elif title:
        books = Book.query.filter(Book.title.contains(title)).paginate(page=page, per_page=per_page)
    elif author:
        books = Book.query.filter(Book.authors.contains(author)).paginate(page=page, per_page=per_page)
    else:
        books = Book.query.paginate(page=page, per_page=per_page)

    return jsonify({
        "books": book_schema.dump(books.items, many=True),
        # "pagination": books.pagination_dict
    })

@book.route("/books/<int:id>", methods=["GET"])
def get_book(id):
    book = Book.query.get(id)
    return jsonify(book_schema.dump(book))

@book.route("/books", methods=["POST"])
def create_books():
    data = request.json
    # Validate the data
    if not data:
        return jsonify({"message": "No data was provided"})
    for book in data["books"]:
        if not book["bookID"]:
            return jsonify({"message": "bookID is required"})
        if not book["title"]:
            return jsonify({"message": "Title is required"})
        if not book["authors"]:
            return jsonify({"message": "Authors is required"})
        if not book["isbn"]:
            return jsonify({"message": "ISBN is required"})
        if not book["isbn13"]:
            return jsonify({"message": "ISBN13 is required"})
        if not book["language_code"]:
            return jsonify({"message": "Language code is required"})
        if not book["num_pages"]:
            return jsonify({"message": "Number of pages is required"})
        if not book["publication_date"]:
            return jsonify({"message": "Publication date is required"})
        if not book["publisher"]:
            return jsonify({"message": "Publisher is required"})

        book = Book(bookID=book["bookID"],title=book["title"], authors=book["authors"], isbn=book["isbn"], isbn13=book["isbn13"], language_code=book["language_code"], num_pages=book["num_pages"], publication_date=book["publication_date"], publisher=book["publisher"])
        db.session.add(book)
    db.session.commit()
    return jsonify({"message": "Books created successfully"})


@book.route("/books/<int:id>", methods=["PUT"])
def update_book(id):
    data = request.json
    # Validate the data
    if not data["bookId"]:
        return jsonify({"message": "bookId is required"})
    if not data["title"]:
        return jsonify({"message": "Title is required"})
    if not data["authors"]:
        return jsonify({"message": "Authors is required"})
    if not data["isbn"]:
        return jsonify({"message": "ISBN is required"})
    if not data["isbn13"]:
        return jsonify({"message": "ISBN13 is required"})
    if not data["language_code"]:
        return jsonify({"message": "Language code is required"})
    if not data["num_pages"]:
        return jsonify({"message": "Number of pages is required"})
    if not data["publication_date"]:
        return jsonify({"message": "Publication date is required"})
    if not data["publisher"]:
        return jsonify({"message": "Publisher is required"})

    book = Book.query.get(id)
    book.bookId = data["bookId"]
    book.title = data["title"]
    book.authors = data["authors"]
    book.isbn = data["isbn"]
    book.isbn13 = data["isbn13"]
    book.language_code = data["language_code"]
    book.num_pages = data["num_pages"]
    book.publication_date = data["publication_date"]
    book.publisher = data["publisher"]
    db.session.commit()
    return jsonify(book_schema.dump(book))

@book.route("/books/<int:id>", methods=["DELETE"])
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"})

# Create the marshmallow schema

class BookStockSchema(schema.Schema):
    class Meta:
        model = BookStock
        fields = ("id", "book_id", "quantity")


# Create the blueprint

book_stock = Blueprint("book_stock", __name__)

# Create the marshmallow instance

book_stock_schema = BookStockSchema()

# Create the routes

@book_stock.route("/book_stocks", methods=["GET"])
def get_book_stocks():
    book_stocks = BookStock.query.all()
    return jsonify(book_stock_schema.dump(book_stocks, many=True))

@book_stock.route("/book_stocks/<int:id>", methods=["GET"])
def get_book_stock(id):
    book_stock = BookStock.query.get(id)
    return jsonify(book_stock_schema.dump(book_stock))

@book_stock.route("/book_stocks", methods=["POST"])
def create_book_stock():
    data = request.json
    # Validate the data
    if not data["book_id"]:
        return jsonify({"message": "Book ID is required"})
    if not data["quantity"]:
        return jsonify({"message": "Quantity is required"})

    book_stock = BookStock(book_id=data["book_id"], quantity=data["quantity"])
    db.session.add(book_stock)
    db.session.commit()
    return jsonify(book_stock_schema.dump(book_stock))

@book_stock.route("/book_stocks/<int:id>", methods=["PUT"])
def update_book_stock(id):
    data = request.json
    # Validate the data
    if not data["book_id"]:
        return jsonify({"message": "Book ID is required"})
    if not data["quantity"]:
        return jsonify({"message": "Quantity is required"})

    book_stock = BookStock.query.get(id)
    book_stock.book_id = data["book_id"]
    book_stock.quantity = data["quantity"]
    db.session.commit()
    return jsonify(book_stock_schema.dump(book_stock))

@book_stock.route("/book_stocks/<int:id>", methods=["DELETE"])
def delete_book_stock(id):
    book_stock = BookStock.query.get(id)
    db.session.delete(book_stock)
    db.session.commit()
    return jsonify({"message": "Book stock deleted"})