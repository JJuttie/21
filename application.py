import smtplib

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context

import os
from werkzeug.utils import secure_filename
from tempfile import mkdtemp

import random

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
    id = session["user_id"]
    # alle gebruikers behalve gebruiker zelf selecteren
    users = db.execute("SELECT id FROM recipes WHERE id!=:id", id=id)
    # alle gebruikers in een lijst zetten
    userlist = [int(id) for id in str(users) if id.isdigit()]
    # willekeurige gebruiker uitkiezen
    user = random.choice(userlist)
    # random gebruiker selecteren werkt zodra id=id wordt veranderd naar id=user
    gerecht = db.execute("SELECT * FROM recipes WHERE id=:id", id=user)
    # session["likedid"] = gerecht[0]["id"]
    imageid = gerecht[0]["imageid"]
    title = gerecht[0]["title"]
    bio = gerecht[0]["bio"]
    tags = [tag for tag in gerecht[0] if gerecht[0][tag]==1]
    tags = ", ".join(tags)
    return render_template("index.html", imageid=imageid, title=title, bio=bio, tags=tags)

@app.route("/like", methods=["GET", "POST"])
@login_required
def like():
    if request.method == "POST":
        db.execute("INSERT INTO like(currentid, likedid) VALUES(currentid=:currentid, likedid=:likedid)", currentid=session["user_id"], likedid=session["likedid"])
        return render_template("index.html")
    else:
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
        id =rows[0]["id"]
        session["user_id"] = id

        recipe = db.execute("SELECT * FROM recipes WHERE id=:id", id=id)
        if not recipe:
            return redirect(url_for("recipe"))
        else:
        # redirect user to home page
            return redirect(url_for("index"))

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
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        #nu ingelogd:
        session["user-id"] = rows[0]["id"]
        # redirect user to home page
        return redirect(url_for("recipe"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    """Forgot password"""

    if request.method == "POST":

        if not request.form.get("email"):
            return apology("please provide your e-mail address")

        elif not request.form.get("town"):
            return apology("please provide your town")

        elif not request.form.get("name"):
            return apology("please provide your name")

        elif not request.form.get("new password"):
            return apology("please provide new password")

        elif not request.form.get("confirmation"):
            return apology("please confirm new password")

        elif request.form.get("new password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        user = db.execute("SELECT * FROM users WHERE email = :email", \
                            email=request.form.get("email"))


        if (user[0]["email"]) != request.form.get("email") and (user[0]["name"]) != request.form.get("name") and (user[0]["town"]) != request.form.get("town"):
            return apology("not valid")
        else:
            hash = pwd_context.hash(request.form.get("new password"))
            db.execute("UPDATE users SET hash = :hash WHERE email = :email", \
                    hash=hash, email=request.form.get("email"))
            flash("New password set!")
            return render_template("login.html")
    else:
        return render_template("forgot.html")
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
        UPLOAD_FOLDER = './static/images'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        id = session["user_id"]
        # Checken of afbeelding is geupload
        if not request.files.get('image', None):
            return apology("You must provide an image!")
        # User input verzamelen
        title = request.form.get("title")
        bio = request.form.get("bio")
        image = request.files["image"]
        tags = request.form.getlist("tags")


        # Checken of user input klopt
        if not title:
            return apology("You must provide an title")
        if not bio:
            return apology("You must provide an bio")

        # update tags in database
        for tag in tags:
            db.execute("UPDATE recipes SET :tag = 1 WHERE id=:id", id=id, tag=tag)

        # naam van de afbeelding ophalen
        filename = secure_filename(image.filename)
        # afbeelding opslaan
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # afbeeldingstype achterhalen
        filetype = filename[filename.rfind("."):]
        # afbeelding hernoemen
        os.rename("static/images/"+filename, "static/images/"+str(id)+filetype)
        # imageid voor in de database vormen
        imageid = "static/images/"+str(id)+filetype
        # alles in de database gooien
        db.execute("INSERT INTO recipes(id, title, bio, imageid) VALUES(:id, :title, :bio, :imageid)", id=id, title=title, bio=bio, imageid=imageid)
        return redirect(url_for("index"))

    else:
        return render_template("recipe.html")

@app.route("/matches", methods=["GET", "POST"])
@login_required
def matches():
    return render_template("matches.html")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    gegevens = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
    email = gegevens[0]['email']
    name = gegevens[0]['name']
    town = gegevens[0]['town']
    return render_template("account.html", email=email, name=name, town=town)

@app.route("/changerecipe", methods=["GET", "POST"])
@login_required
def changerecipe():
    """change recipe"""
    if request.method == "POST":
        UPLOAD_FOLDER = './static/images'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        id = session["user_id"]
        # Checken of afbeelding is geupload
        if not request.files.get('image', None):
            return apology("You must provide an image!")
        # User input verzamelen
        title = request.form.get("title")
        bio = request.form.get("bio")
        image = request.files["image"]
        tags = request.form.getlist("tags")

        # Checken of user input klopt
        if not title:
            return apology("You must provide an title")
        if not bio:
            return apology("You must provide an bio")

        # reset all tags
        db.execute("UPDATE recipes SET corn = NULL, egg = NULL, fish = NULL, meat = NULL, milk = NULL,	peanut = NULL, shellfish = NULL, soy = NULL, 'tree nut' = NULL, wheat = NULL, FPIES = NULL")
        # update tags in database
        for tag in tags:
            db.execute("UPDATE recipes SET :tag = 1 WHERE id=:id", id=id, tag=tag)

        # naam van de afbeelding ophalen
        filename = secure_filename(image.filename)
        # type van de afbeelding ophalen
        filetype = filename[filename.rfind("."):]
        # de oude file van gebruiker ophalen en verwijderen
        oldfile = db.execute("SELECT imageid FROM recipes WHERE id=:id", id=id)
        os.remove(oldfile[0]["imageid"])
        # nieuwe file opslaan
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # afbeelding hernoemen
        os.rename("static/images/"+filename, "static/images/"+str(id)+filetype)
        imageid = "static/images/"+str(id)+filetype
        # alles in de database gooien
        db.execute("UPDATE recipes SET title=:title, bio=:bio, imageid=:imageid WHERE id=:id", id=id, title=title, bio=bio, imageid=imageid)
        return redirect(url_for("index"))

    else:
        return render_template("changerecipe.html")


