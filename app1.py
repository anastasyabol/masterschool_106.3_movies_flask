from flask import Flask, render_template, request, redirect, url_for, flash
from os import getenv
from datamanager.json_data_manager import *
from werkzeug.security import generate_password_hash, check_password_hash
from users.users_login import User
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY", default="secret_key_example")
data_manager = JSONDataManager('datamanager/movies_data.json')  # Use the appropriate path to your JSON file
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id: str):
    """User loader function for Flask-Login to load a user given the user_id"""
    return User.get(user_id)


# INDEX PAGE
@app.route('/')
def index():
    """Default route for the index page. Getting a random movie from the data manager for index page"""
    flash("Random movie for tonight...")
    random_movie = random.choice(data_manager.get_user_movies(0))
    username = current_user.username if current_user.is_authenticated else "anonymous"
    user_id = current_user.id if current_user.is_authenticated else None
    return render_template('index.html', username=username, user_id=user_id, movie=random_movie)


# REGISTER

@app.route("/register", methods=["POST", "GET"])
def register():
    """Route for user registration, if the user is already authenticated, redirect to the index page"""
    if current_user.is_authenticated:
        redirect(url_for("index"))
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['psw']

        if len(name) > 2 and len(email) > 4 and "@" in email and len(password) >= 6:
            email_exist = User.get_email(email)

            if email_exist is None:
                hashed_password = generate_password_hash(password)
                new_user_id = User.add_user(name, email, hashed_password)
                data_manager.add_new_user(new_user_id, name)
                return redirect(url_for('login'))
            else:
                flash("Email already exists. Please try a different email.")
                return redirect(request.url)
        else:
            flash("Name should be longer than 2 symbols, email longer than 4, pass longer than 6")

    return render_template("register.html", username="anonymous"), 200


# LOGIN
@app.route("/login", methods=["POST", "GET"])
def login():
    """Route for user login. If the user is already authenticated, redirect to the index page"""
    if current_user.is_authenticated:
        redirect(url_for("index"))
    if request.method == "POST":
        user_email = request.form['email']
        user_pass = request.form['psw']
        user = User.get_email(user_email)
        if user is not None and check_password_hash(user.password, user_pass):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Wrong email or password")
            return redirect(request.url)
    else:
        flash(
            "Test users are: lena@lena.ru or ana@bolshem.com pass: 123456 (hashed),"
            " but you're welcome to create one of your own ")
        return render_template('login.html')


# LOGOUT
@app.get("/logout")
@login_required
def logout():
    """Route for user logout"""
    logout_user()
    return redirect(url_for("index"))


# USER MAIN PAGE AND ADD NEW MOVIE
@app.route("/user/<int:id>", methods=["POST", "GET"])
@login_required
def user_movies(id: int, sort: int = 0):
    """Route for the user's main page and adding a new movie. Get the user's movies from the data manager
    If the user ID doesn't match the current user's ID, render an error page with 403 status code
    Using Status object (enum) for statuses of added movies"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    user_movies = data_manager.get_user_movies(id, sort)
    if len(user_movies) == 0:
        user_movies = None
    if request.method == "POST":
        new_movie = request.form['title']
        status = data_manager.add_new_movie(int(current_user.id), new_movie)
        if status == Status.ALREADY_ADDED:
            flash('Movie already in the library')
            return redirect(request.url)
        elif status == Status.NOT_FOUND:
            flash('Movie not found. Please try again')
            return redirect(request.url)
        elif status == Status.OK:
            flash('Added')
            return redirect(request.url)
    else:
        return render_template('users_movie.html', username=current_user.username, movies=user_movies,
                               user_id=current_user.id)


# UPDATE
@app.route("/user/<int:id>/update/<int:movie_id>", methods=["GET", "POST"])
@login_required
def update_movie(id: int, movie_id: int):
    """Route for updating a movie.
    If the user ID doesn't match the current user's ID, render an error page with 403 status code
    Get the movie information from the data manager and sends it to be rendered in the form
    Gets new info from the user input, validates it and updates data manager"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    movie_data = data_manager.movie_info(int(current_user.id), movie_id)
    if movie_data is None:
        return render_template('error.html', error=404, username=current_user.username, user_id=current_user.id), 404
    title = movie_data.get('name')
    director = movie_data.get('director')
    year = movie_data.get('year')
    rating = movie_data.get('rating')
    img = movie_data.get('img')
    imdbID = movie_data.get('imdbID')
    notes = movie_data.get('notes', "")
    if request.method == "POST":
        title_upd = request.form['title']
        director_upd = request.form['director']
        year_upd = request.form['year']
        rating_upd = request.form['rating']
        notes_upd = request.form['notes']
        # Check if the title and director fields are empty
        if title_upd == "" or director_upd == "":
            flash("Title/Director can't be emty")
            return redirect(request.url)
        # Check if the rating might be converted to float
        try:
            float(rating_upd)
        except ValueError:
            flash("Rating must be a number")
            return redirect(request.url)
        # Check if the year has the correct format
        if len(year_upd) != 4 and len(year_upd) != 9:
            flash("Year must be xxxx or xxxx-xxxx")
            return redirect(request.url)
        data_manager.movie_update(id, movie_id, title_upd, director_upd, year_upd, rating_upd, notes_upd)
        flash(f' {title_upd} updated')
        return redirect(url_for("user_movies", id=current_user.id))
    else:
        flash(f'Update {title}')
        return render_template('update.html', user_id=current_user.id, username=current_user.username,
                               movie_id=movie_id, title=title, director=director, year=year, rating=rating, notes=notes,
                               img=img, imdbID=imdbID)


# DELETE
@app.route("/user/<int:id>/delete/<int:movie_id>", methods=["GET"])
@login_required
def delete(id: int, movie_id: int):
    """Route for updating a movie.
     If the user ID doesn't match the current user's ID, render an error page with 403 status code
     Checks if movie exists (if not: error 404) and delete the movie from the data manager"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    if not data_manager.delete_movie(int(current_user.id), movie_id):
        return render_template('error.html', error=404, username=current_user.username, user_id=current_user.id), 404
    else:
        flash("Movie deleted")
        return redirect(url_for("user_movies", id=current_user.id))


# SORT
@app.route("/user/<int:id>/sort/<int:sort>", methods=["GET"])
@login_required
def sort_movies(id: int, sort: int):
    """ Route for sorting user's movies. Sort the user's movies based on the given sort parameter
     If the user ID doesn't match the current user's ID, render an error page with 403 status code"""
    if id != int(current_user.id):
        return render_template('error.html', error=403, username=current_user.username, user_id=current_user.id), 403
    return user_movies(id, sort)


if __name__ == '__main__':
    User.load_users("users/users.json")
    app.run(debug=True)
