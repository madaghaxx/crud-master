import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_USER = os.getenv('INVENTORY_DB_USER')
DB_PASS = os.getenv('INVENTORY_DB_PASSWORD')
DB_HOST = os.getenv('INVENTORY_DB_HOST')
DB_PORT = os.getenv('INVENTORY_DB_PORT')
DB_NAME = os.getenv('INVENTORY_DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }
    
with app.app_context():
    db.create_all()