#app.py
from flask import Flask, jsonify, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from schemas import movies_schema, movie_schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
directors_ns = api.namespace('directors')

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

@movie_ns.route("/")
class MovieView(Resource):
    def get(self):
        all_movies = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
                                      Genre.name.label('genre'),
                                      Director.name.label('director')).join(Genre).join(Director).all()

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')

        if director_id:
            all_movies.filter(Movie.director_id == director_id)
        if genre_id:
            all_movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json()
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый объект с id {new_movie.id} создан", 201



@movie_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid):
        movie = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
                         Genre.name.label('genre'),
                         Director.name.label('director')).join(Genre).join(Director).filter(
            Movie.id == mid).first()
        if movie:
            return movie_schema.dump(movie)
        return "Нет такого фильма", 404

    def patch(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if  not movie:
            return "Нет такого фильма", 404

        req_json = request.json
        if 'title' in req_json:
            movie.title = req_json['title']
        elif 'description' in req_json:
            movie.description = req_json['description']
        elif 'trailer' in req_json:
            movie.trailer = req_json['trailer']
        elif 'year' in req_json:
            movie.year = req_json['year']
        elif 'rating' in req_json:
            movie.rating = req_json['rating']
        elif 'genre_id' in req_json:
            movie.genre_id = req_json['genre_id']
        elif 'director_id' in req_json:
            movie.director_id = req_json['director_id']
        db.session.ad(movie)
        db.session.commit()
        return f"Объект с id {movie.id} обновлен", 204

    def put(self, mid):
        movie = db.session.query(Movie).get(mid)
        if movie:
            return "Нет такого фильма", 404
        req_json = request.json()

        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']
        db.session.ad(movie)
        db.session.commit()
        return f"Объект с id {movie.id} обновлен", 204

    def delete(self, mid):
        movie = db.session.query(Movie).get(mid)
        if movie:
            return "Нет такого фильма", 404
        db.session.delete(movie)
        db.session.commit()
        return f"Объект с id {movie.id} удален", 204



if __name__ == '__main_rating__':
    app.run(debug=True)
