import os
from flask import Flask
from .extensions import db, migrate
from .routes.member import member
from .routes.book import book
from .routes.rental import rental
from .routes.index import index
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    load_dotenv()

    db_uri = os.getenv("POSTGRESQL_URI")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(member)
    app.register_blueprint(book)
    app.register_blueprint(index)
    app.register_blueprint(rental)
    return app
