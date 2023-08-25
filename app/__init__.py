from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///comap_manchester_database.db'
db = SQLAlchemy(app)

from . import views  # This ensures your routes are loaded
