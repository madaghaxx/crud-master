import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from dotenv import load_dotenv

dotenv_path = '/vagrant/.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
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

@app.route('/api/movies', methods=['GET'])
def get_movies():
    title = request.args.get('title')
    if title:
        stmt = select(Movie).where(Movie.title.ilike(f'%{title}%'))
    else:
        stmt = select(Movie)
    movies = db.session.scalars(stmt).all()
    return jsonify([m.to_dict() for m in movies]), 200

@app.route('/api/movies', methods=['POST'])
def create_movie():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('description'):
        return jsonify({"error": "Title and description are required"}), 400

    new_movie = Movie(
        title=data['title'],
        description=data['description']
    )
    db.session.add(new_movie)
    db.session.commit()
    return jsonify(new_movie.to_dict()), 201

@app.route('/api/movies', methods=['DELETE'])
def delete_all_movies():
    db.session.query(Movie).delete()
    db.session.commit()
    return jsonify({"message": "All movies deleted"}), 200

@app.route('/api/movies/<int:id>', methods=['GET'])
def get_movie(id):
    movie = db.session.get(Movie, id)
    if movie is None:
        return jsonify({"error": "Movie not found"}), 404
    return jsonify(movie.to_dict()), 200

@app.route('/api/movies/<int:id>', methods=['PUT'])
def update_movie(id):
    movie = db.session.get(Movie, id)
    if movie is None:
        return jsonify({"error": "Movie not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    movie.title = data.get('title', movie.title)
    movie.description = data.get('description', movie.description)
    db.session.commit()
    return jsonify(movie.to_dict()), 200

@app.route('/api/movies/<int:id>', methods=['DELETE'])
def delete_movie(id):
    movie = db.session.get(Movie, id)
    if movie is None:
        return jsonify({"error": "Movie not found"}), 404
    db.session.delete(movie)
    db.session.commit()
    return jsonify({"message": f"Movie {id} deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)