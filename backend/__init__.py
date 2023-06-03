from flask import Flask
from .extensions import db, migrate
from .routes.member import member
from .routes.book import book
from .routes.rental import rental
from .routes.index import index

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://vishakhdesai:q8I7X5M4ae8L1nQDhJcoU3Cw9W7zEap1@dpg-chtd485269vccp4sugd0-a.oregon-postgres.render.com/library_records"
    db.init_app(app)
    migrate.init_app(app,db)
    app.register_blueprint(member)
    app.register_blueprint(book)
    app.register_blueprint(index)
    app.register_blueprint(rental)
    return app