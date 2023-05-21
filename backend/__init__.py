from flask import Flask
from .extensions import db
from .routes.member import member
from .routes.book import book

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5433/library-records"
    db.init_app(app)
    app.register_blueprint(member)
    app.register_blueprint(book)
    return app