import numpy as np
from flask import Flask
import flask
import os
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from fileinput import filename
from flask import Blueprint,render_template, request, flash, redirect
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from unicodedata import name
from sqlalchemy import nullslast
from flask_login import UserMixin
from sqlalchemy.sql import func
from collections.abc import Mapping
from flask import Flask, render_template, redirect, request, session

import cv2


db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = 'static/uploads/'



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship('Post', backref='user', passive_deletes=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)

def create_database(app):
    # if not path.exists("website/" + DB_NAME):
    with app.app_context():
        db.create_all()
        # db.create_all(app=app)
        print("Created database!")

def create_app(debug=True):
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)


    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

app = create_app()



age=""
option2=""
option3=""
option4=""
option5=""
risk=0
result_binary=0
# app = Blueprint("app", __name__)
# UPLOAD_FOLDER = 'static/uploads/'
#flask.current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
@app.route("/face")
@login_required
def face():
    return render_template("index.html",user=current_user)

@app.route("/home")
@login_required
def home():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    # posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


@app.route("/q")
@login_required
def q():
    questions = ["Are you having headache?","Balance: Are you leaning to one side or staggering when walking?","Eyes:Is there a sudden loss of vision in one or both eyes?","Arms:Raise your both arms. Does one arm drift downward?"]
    return render_template("q.html",user=current_user)



@app.route('/detect', methods=['POST'])
def detect():
    # Get the captured image from the POST request
    img_data = request.files['image'].read()

    # Convert the image data to a numpy array
    nparr = np.frombuffer(img_data, np.uint8)

    # Decode the numpy array into an OpenCV image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Load the face cascade classifier
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Perform face droop detection
    result = "Face droop not detected"
    global result_binary
    result_binary=0

    for (x, y, w, h) in faces:
        nose_point = (x + int(w/2), y + int(h/2))
        chin_point = (x + int(w/2), y + h)

        # Calculate the distance between the nose and chin points
        distance = abs(chin_point[1] - nose_point[1])

        # Determine if the face is drooping based on the distance and threshold
        threshold = 0.6  # Adjust this value as needed
        if distance >= threshold * h:
            result = "Face droop detected"
            result_binary=1
            break

    return result


@app.route("/q1",methods =["GET", "POST"])
@login_required
def q1():
    # if request.method == "POST":
    #    global age
    #    global risk
    #    age1 = request.form.get("age")
    #    age = age1
       
    #    return "Your age is "+age1
    return render_template("q1.html",user=current_user)

@app.route("/q2",methods =["GET", "POST"])
@login_required
def q2():
    if request.method == 'POST':       
        global age
        global risk
        age1 = request.form.get("age")
        age = age1
        # if age>40:
        #    risk = 0.2
        return render_template("q2.html",user=current_user, age=age)

@app.route("/q3",methods =["GET", "POST"])
@login_required
def q3():
    global option2
    global risk
    option2 = request.form.get('headache')
    # if option2=="yes":
    #     risk=risk+0.2
    return render_template("q3.html",user=current_user)

@app.route("/q4",methods =["GET", "POST"])
@login_required
def q4():
    global option3
    global risk
    option3 = request.form.get('balance')
    # if option3=="yes":
    #     risk=risk+0.2
    return render_template("q4.html",user=current_user)

@app.route("/q5",methods =["GET", "POST"])
@login_required
def q5():
    global option4
    global risk
    option4 = request.form.get('eye')
    return render_template("q5.html",user=current_user)

@app.route("/risk",methods =["GET", "POST"])
@login_required
def risk():
    global age
    global option2
    global option3
    global option4
    global option5
    global risk
    option5 = request.form.get('arms')
    if int(age)>40:
           risk = 0.2
    if option2=="yes":
        risk+=0.2
    if option3=="yes":
        risk+=0.2
    if option4=="yes":
        risk+=0.2
    if option5=="yes":
        risk+=0.2
    return render_template("risk.html",user=current_user,risk=round(risk,2), face_risk=result_binary)


@app.route("/qna")
@login_required
def qna():
    questions = ["Are you having headache?","Balance: Are you leaning to one side or staggering when walking?","Eyes:Is there a sudden loss of vision in one or both eyes?","Arms:Raise your both arms. Does one arm drift downward?"]
    return render_template("qna.html",user=current_user, questions=questions)

@app.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        pic = request.files['pic']

        text = request.form.get('text')

        if not pic:
            flash('No image uploaded!')
        if not text:
            flash('Post caption cannot be empty', category='error')
        else:
            filename= secure_filename(pic.filename)
            pic.save(os.path.join(flask.current_app.config['UPLOAD_FOLDER'],filename))
            mimetype= pic.mimetype

            post = Post(img=pic.read(),mimetype = mimetype,name = filename,text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(('/home'))

    return render_template('create_post.html', user=current_user)


@app.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    # elif current_user.id != post.id:
    #     flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(('/home'))


@app.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(('/home'))

    posts = Post.query.filter_by(author=user.id).order_by(Post.date_created.desc()).all()
    return render_template("posts.html", user=current_user, posts=posts, username=username)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                # flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('q'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@app.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('login'))

    return render_template("signup.html", user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":   
    app.run(debug=True)