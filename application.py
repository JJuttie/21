import smtplib

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context

import os
from werkzeug.utils import secure_filename
from tempfile import mkdtemp

from Mike import *
from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///foodiematch.db")

def reset():

    """Sending email for password reset"""

    gmail_user = "foodiematch21@gmail.com"
    gmail_pwd = "FoodieMatch21#"
    TO = request.form.get("email")
    SUBJECT = "Password reset"
    message = "Use this link to reset your password"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    BODY = '\r\n'.join(['To: %s' % TO,
            'From: %s' % gmail_user,
            'Subject: %s' % SUBJECT,
            '', message])
    server.sendmail(gmail_user, [TO], BODY)


@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for email
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        # ensure email exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid email and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return render_template("index.html")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        gmail_user = "foodiematch21@gmail.com"
        gmail_pwd = "FoodieMatch21#"
        TO = request.form.get("email")
        SUBJECT = "Registration confirmation"
        message = "Thank you for registering on FoodieMatch!"
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        BODY = '\r\n'.join(['To: %s' % TO,
                'From: %s' % gmail_user,
                'Subject: %s' % SUBJECT,
                '', message])
        server.sendmail(gmail_user, [TO], BODY)

        # provide email
        if not request.form.get("email"):
            return apology("You must provide an email.")

        # provide name
        elif not request.form.get("name"):
            return apology("must provide your name")

        # provide town
        elif not request.form.get("town"):
            return apology("must provide your town")

        # provide password
        elif not request.form.get("password"):
            return apology("must provide a password")

        # provide password again
        elif not request.form.get("confirmation"):
            return apology("must provide a confirmation password")

        # checken
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("wachtwoorden zijn niet gelijk aan elkaar")

        #wachtwoord encrypten
        password=pwd_context.hash(request.form.get("password"))

        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))
        if len(rows) != 0:
            return apology("email already used")

        # pomp het in de database
        gebruiker = db.execute("INSERT INTO users(email, name, town, hash) VALUES(:email, :name, :town, :hash)",
        email=request.form.get("email"), name=request.form.get("name"), town=request.form.get("town"), hash=password)

        #nu ingelogd:
        session["user-id"] = gebruiker
        # redirect user to home page
        return render_template("recipe.html")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


#extra_opdracht2
@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change your password"""
    if request.method == "POST":
        # wachtwoord opgeven
        if not request.form.get("new"):
            return apology("vul je nieuwe wachtwoord in")

        # wachtwoord bevestigen
        elif not request.form.get("confirmation"):
            return apology("vul je bevestiging in")

        #checken of de nieuwe hetzelfde zijn
        if request.form.get("new") != request.form.get("confirmation"):
            return apology("nieuwe wachtwoorden zijn niet gelijk aan elkaar")

        #database updaten
        db.execute("UPDATE users SET hash =:hash WHERE \
        id=:id", id=session["user_id"], hash=pwd_context.hash(request.form.get("confirmation")))

        return redirect(url_for("index"))

    else:
        return render_template("password.html")

@app.route("/recipe", methods=["GET", "POST"])
@login_required
def recipe():
    """add recipe to profile"""
    if request.method == "POST":
        UPLOAD_FOLDER = './images'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        # UPLOAD_FOLDER = os.path.basename('uploads')
        id = session["user_id"]
        # User input verzamelen
        title = request.form.get("title")
        bio = request.form.get("bio")
        image = request.files["image"]

        # Checken of user input klopt
        if not title:
            return apology("You must provide an title")
        if not bio:
            return apology("You must provide an bio")
        # still have to write check if user has uploaded image!!
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return apology("done")
        db.execute("INSERT INTO users(id, title, bio, imagebinary) VALUES(:id, :title, :bio, :imagebinary", id=id, title=title, bio=bio, imagebinary=imagebinary)
    else:
        return render_template("recipe.html")

    # """Recipe tijdens registratie"""
    # if request.method == "POST":

    #     # provide image
    #     if not request.form.get("image"):
    #         return apology("You must provide an image.")

    #     # provide title
    #     elif not request.form.get("title"):
    #         return apology("must provide a title")

    #     # provide bio
    #     elif not request.form.get("bio"):
    #         return apology("must provide a bio")

    #     # provide tags
    #     elif not request.form.get("tags"):
    #         return apology("must provide tags")

    #     # pomp het in de database
    #     db.execute("INSERT INTO recipes(id, image, title, bio, tags) VALUES(:id, :image, :title, :bio, :tags)",
    #     id=session["user-id"], image=request.form.get("title"), title=request.form.get("title"),
    #     bio=request.form.get("bio"), tags=request.form.get("tags"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    # else:
    #     return render_template("recipe.html")

    #     # redirect user to home page
    #     return render_template("login.html")

    # # else if user reached route via GET (as by clicking a link or via redirect)
    # else:
    #     return render_template("recipe.html")
