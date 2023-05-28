from flask import Blueprint, jsonify, request, render_template, request, redirect, url_for, flash
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import schema
from ..extensions import db
from ..models.book import Book

index = Blueprint("index", __name__)

@index.route("/", methods = ["GET"])
def home():
    return render_template("index.html")