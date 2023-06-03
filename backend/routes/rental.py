from flask import Blueprint, jsonify, request, render_template
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.member import Member
from ..models.rental import Rental, BookRental
from ..models.book import Book
from datetime import date, datetime

class BookSchema(schema.Schema):
    class Meta:
        model = Book
        fields = (
            "id", "bookID", "title", "authors", "average_rating", "isbn", "isbn13",
            "language_code", "num_pages", "ratings_count", "text_reviews_count",
            "publication_date", "publisher", "quantity"
        )

book_schema = BookSchema()
# Create the marshmallow schema

class RentalSchema(schema.Schema):
    class Meta:
        model = Rental
        fields = ("id", "member_id", "start_date", "end_date", "rent_fee")


# Create the blueprint

rental = Blueprint("rental", __name__)

# Create the marshmallow instance

rental_schema = RentalSchema()

# Create the routes


@rental.route("/rent-books/<int:member_id>", methods=["GET"])
def get_rent_book(member_id):
    try:
        page = int(request.args.get("page", 1))
        title = request.args.get("title")
        authors = request.args.get("authors")
        per_page = int(request.args.get("per_page", 20))

        if title and authors:
            books = Book.query.filter(Book.title.contains(title) & Book.authors.contains(authors), Book.quantity > 0).paginate(page=page, per_page=per_page)
        elif title:
            books = Book.query.filter(Book.title.contains(title), Book.quantity > 0).paginate(page=page, per_page=per_page)
        elif authors:
            books = Book.query.filter(Book.authors.contains(authors), Book.quantity > 0).paginate(page=page, per_page=per_page)
        else:
            books = Book.query.filter(Book.quantity > 0).paginate(page=page, per_page=per_page)
        total_pages = books.pages
        books = book_schema.dump(books.items, many=True)
        member = Member.query.get(member_id)
        in_list_book_ids = []
        is_book_selected = True
        if(member.issue_list == "" or member.issue_list == None):
            is_book_selected = False
        else:
            in_list_book_ids = member.issue_list.split(',')
        rentals = Rental.query.filter(Rental.member_id == member_id, Rental.book_returned == False).all()
        issued_books_ids = []
        for rental in rentals:
            for book_rental in rental.book_rentals:
                issued_books_ids.append(str(book_rental.book_id))
        for book in books:
            if str(book["id"]) in in_list_book_ids:
                book["is_in_list"] = True
                book["is_issued"] = False
            elif str(book["id"]) in issued_books_ids:
                book["is_in_list"] = False
                book["is_issued"] = True
            else:
                book["is_in_list"] = False
                book["is_issued"] = False
        title = request.args.get("title", "")
        authors = request.args.get("authors", "")
        return render_template("rent-books.html", books=books, title=title, authors=authors, total_pages=total_pages, member_id=member_id, is_book_selected=is_book_selected), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@rental.route("/add-to-rental-list<int:member_id>", methods=["POST"])
def add_to_rental_list(member_id):
    try:
        data = request.json
        print(member_id, data)
        member = Member.query.get(member_id)
        if(member.books_issue_limit == 0):
            return jsonify({"message": "A member can only take five books from the library"}), 400
        if(member.issue_list == "" or member.issue_list == None):
            member.issue_list = str(data["bookId"])
        else:
            member.issue_list += "," + str(data["bookId"])
        member.books_issue_limit -= 1
        db.session.commit()
        return jsonify({"message": "success"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@rental.route("/checkout/<int:member_id>", methods=["GET"])
def get_checkout(member_id):
    try:
        member = Member.query.get(member_id)
        issue_books = []
        if(member.issue_list):
            book_ids = member.issue_list.split(',')
        else:
            return get_rent_book(member_id)
        for book_id in book_ids:
            book = Book.query.get(book_id)
            issue_books.append(book)
        return render_template("checkout.html", books=issue_books, member_id=member_id)
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@rental.route("/remove_from_rental_list/<int:member_id>", methods=["DELETE"])
def remove_from_rental_list(member_id):
    try:
        data = request.json
        print(member_id, data)
        member = Member.query.get(member_id)
        bookIds = member.issue_list.split(",")
        bookIds.remove(str(data["bookId"]))
        if(bookIds == []):
            member.issue_list = None
        else:
            member.issue_list = ",".join(bookIds)
        member.books_issue_limit += 1
        db.session.commit()
        return jsonify({"message": "success"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@rental.route("/issue_books/<int:member_id>", methods=["POST"])
def issue_books(member_id):
    try:
        member = Member.query.get(member_id)
        if(member.outstanding_debt >= 500):
            return jsonify({"message": "Member's Outstanding Debt is more than ₹500"}), 400
        books = []
        data = request.json
        for b in data["books"]:
            book = Book.query.get(b["bookId"])
            if(book.quantity == 0):
                msg = "Book titled: " + book.title + " is currently out of stock"
                return jsonify(msg), 400
            books.append((book, int(b["fee"])))

        rental = Rental(
            member_id=member_id,
            start_date=date.today(),
            book_returned=False,
            total_rent_fee=0
        )
        print(rental)
        db.session.add(rental)
        for book in books:
            book_rental = BookRental(
                book_id=book[0].id,
                rent_fee=book[1],
                rental=rental
            )
            db.session.add(book_rental)
            book[0].quantity -= 1
        member.issue_list = None
        db.session.commit()
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@rental.route('/rentals')
def view_rentals():
    try:
        rentals = Rental.query.filter(Rental.book_returned == False).all()
        return render_template('rentals.html', rentals=rentals, returned=False)
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@rental.route('/rentals-returned')
def view_returned_rentals():
    try:
        rentals = Rental.query.filter(Rental.book_returned == True).all()
        return render_template('rentals.html', rentals=rentals, returned=True)
    except Exception as e:
        return jsonify({"message": str(e)}), 500    

@rental.route("/calculate-total-fee/<int:rental_id>", methods=["POST"])
def calculate_total_fee(rental_id):
    try:
        rental = Rental.query.get(rental_id)
        return_date = request.json["return_date"]
        return_date = date.fromisoformat(return_date)
        issue_duration = (return_date - rental.start_date).days
        total_fee = 0
        for book_rental in rental.book_rentals:
            total_fee += issue_duration * book_rental.rent_fee

        return jsonify({"total_fee": total_fee, "member_outstanding_debt": rental.member.outstanding_debt}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@rental.route("/return-book/<int:rental_id>", methods=["POST"])
def return_book(rental_id):
    try:
        rental = Rental.query.get(rental_id)
        payment = request.json["payment"]
        total_fee = request.json["total_fee"]
        rental.total_rent_fee = total_fee
        rental.book_returned = True
        rental.end_date = request.json["return_date"]
        member = Member.query.get(rental.member_id)
        member.outstanding_debt += (total_fee - payment)
        if(member.outstanding_debt > 500) :
            extra_payment = member.outstanding_debt - 500
            msg = "Extra Payment of ₹" + extra_payment + "is necessary to keep outstanding debt of member less than 500"
            return jsonify({"message": msg}), 400
        for book_rental in rental.book_rentals:
            book = Book.query.get(book_rental.book_id)
            book.quantity += 1
            member.books_issue_limit += 1
        db.session.commit()
        return jsonify({"message": "success"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@rental.route("/rentals/<int:id>", methods=["GET"])
def get_rental(id):
    try:
        rental = Rental.query.get(id)
        return jsonify(rental_schema.dump(rental))
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@rental.route("/rentals", methods=["POST"])
def create_rental():
    try:
        data = request.json
        # Validate the data
        if not data["book_id"]:
            return jsonify({"message": "Book ID is required"}), 400
        if not data["member_id"]:
            return jsonify({"message": "Member ID is required"}), 400
        if not data["start_date"]:
            return jsonify({"message": "Start date is required"}), 400
        if not data["end_date"]:
            return jsonify({"message": "End date is required"}), 400

        rental = Rental(book_id=data["book_id"], member_id=data["member_id"], start_date=data["start_date"], end_date=data["end_date"])
        db.session.add(rental)
        db.session.commit()
        return jsonify(rental_schema.dump(rental)), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@rental.route("/rentals/<int:id>", methods=["PUT"])
def update_rental(id):
    try:
        data = request.json
        # Validate the data
        if not data["book_id"]:
            return jsonify({"message": "Book ID is required"}), 400
        if not data["member_id"]:
            return jsonify({"message": "Member ID is required"}), 400
        if not data["start_date"]:
            return jsonify({"message": "Start date is required"}), 400
        if not data["end_date"]:
            return jsonify({"message": "End date is required"}), 400

        rental = Rental.query.get(id)
        rental.book_id = data["book_id"]
        rental.member_id = data["member_id"]
        rental.start_date = data["start_date"]
        rental.end_date = data["end_date"]
        db.session.commit()
        return jsonify(rental_schema.dump(rental))
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@rental.route("/rentals/<int:id>", methods=["DELETE"])
def delete_rental(id):
    try:
        rental = Rental.query.get(id)
        db.session.delete(rental)
        db.session.commit()
        return jsonify({"message": "Rental deleted"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500
