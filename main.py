from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

# Create a Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# Setting Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lista_movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Integrating Bootstrap
Bootstrap(app)

API_KEY = 'YOUR API KEY'
URL_SEARCH_MOVIE = 'https://api.themoviedb.org/3/search/movie'
URL_FIND_MOVIE = 'https://api.themoviedb.org/3/movie/'

# Integrating SQLAlchemy and Creating Table
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


# Movie rating form
class RateMovie(FlaskForm):
    new_rating = StringField('Sua avaliação: ', validators=[DataRequired()])
    new_review = StringField('Seu review: ', validators=[DataRequired()])
    submit = SubmitField('Editar')


# Form to add movie
class AddMovie(FlaskForm):
    add = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add movie')


# Create routes for Flask Application
@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    return render_template("index.html", movies=all_movies)


# Route to edit rating and review
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    update_form = RateMovie()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if update_form.validate_on_submit():
        movie.rating = float(update_form.new_rating.data)
        movie.review = update_form.new_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=update_form)

# Route to delete movie
@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


# Route to add movie
@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    form = AddMovie()
    if form.validate_on_submit():
        query = form.add.data
        params = {
            'api_key': API_KEY,
            'query': query
        }
        response = requests.get(url=URL_SEARCH_MOVIE, params=params)
        data = response.json()['results']
        return render_template('select.html', movies=data)
    return render_template('add.html', form=form)

# Route to find movie
@app.route('/find')
def find_movie():
    movie_id_API = request.args.get('id')
    if movie_id_API:
        params = {
            'api_key': API_KEY,
            'language': 'pt-br'
        }
        response = requests.get(url=f'{URL_FIND_MOVIE}{movie_id_API}', params=params)
        data = response.json()
        new_movie = Movie(
            title=data['title'],
            img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
            year=data['release_date'].split('-')[0],
            description=data['overview']
        )
        db.session.add(new_movie)
        db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
