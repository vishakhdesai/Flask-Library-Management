from flask import Flask
from .extensions import db, migrate
from .routes.member import member
from .routes.book import book
from .routes.rental import rental
from .routes.index import index

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5433/library-records"
    db.init_app(app)
    migrate.init_app(app,db)
    app.register_blueprint(member)
    app.register_blueprint(book)
    app.register_blueprint(index)
    return app