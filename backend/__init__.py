import os
from flask import Flask, render_template
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
    
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404
    app.register_blueprint(member)
    app.register_blueprint(book)
    app.register_blueprint(index)
    app.register_blueprint(rental)
    return app
app = create_app()