import argparse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from . import app, db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)

class Level1File(db.Model):
    obs_id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(80), nullable=False)
    mjd = db.Column(db.Float, nullable=True)
    year = db.Column(db.String(4), nullable=False)
    month = db.Column(db.String(2), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    mean_Tvane = db.Column(db.Float, nullable=True)
    mean_Tshroud = db.Column(db.Float, nullable=True)
    mean_az = db.Column(db.Float, nullable=True)
    mean_el = db.Column(db.Float, nullable=True)
    mean_wind_speed = db.Column(db.Float, nullable=True)
    mean_air_temp = db.Column(db.Float, nullable=True)
    mean_air_pressure = db.Column(db.Float, nullable=True)
    mean_relative_humidity = db.Column(db.Float, nullable=True)
    mean_wind_direction = db.Column(db.Float, nullable=True)

class Level2File(db.Model):
    obs_id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(80), nullable=False)
    mjd = db.Column(db.Float, nullable=True)
    year = db.Column(db.String(4), nullable=False)
    month = db.Column(db.String(2), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    mean_Tsys = db.Column(db.Float, nullable=True)
    mean_Gain = db.Column(db.Float, nullable=True)

class Figure(db.Model):
    figure_id = db.Column(db.Integer, primary_key=True)
    obs_id = db.Column(db.Integer, db.ForeignKey('level2_file.obs_id'), nullable=False)  # This line was changed
    figure_path = db.Column(db.String(300), nullable=False)

class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    figure_id = db.Column(db.Integer, db.ForeignKey('figure.figure_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    comment_text = db.Column(db.String(500), nullable=True)
    flag = db.Column(db.String(100), nullable=True)

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database_name',type=str, help='Name of the database to create', default='comap_manchester_database.db')
    return parser.parse_args()


    # Database Contents
    # Level 1 data info - source name, obsid, filename, mean Tvane, mean Tshroud, mean az, mean el, mean wind speed 
    # Level 2 data info - source name, obsid, filename, mean Tsys, mean Gain 
def create_all(database_name):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_name}'
    db.create_all()


def run():

    args = options()

    with app.app_context():
        create_all(args.database_name)

if __name__ == '__main__':
    run()