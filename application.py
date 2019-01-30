import smtplib

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

import os
from werkzeug.utils import secure_filename
from tempfile import mkdtemp

import random
import re

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

# configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///foodiematch.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    id = session["user_id"]
    if request.method == "POST":
        likedid = session["likedid"]
        # gegevens in database zetten bij like en pagina herladen
        if request.form["like"] == "like":
            db.execute("INSERT INTO like(currentid, likedid) VALUES(:currentid, :likedid)", currentid=id, likedid=likedid)
            # matches nagaan
            matches = check_matches(id)
            # als match is dan verwijzing naar matches
            if likedid in matches:
                return redirect(url_for("matches"))
            else:
                return redirect(url_for("index"))
        # pagina herladen bij dislike
        elif request.form["like"] == "dislike":
            return redirect(url_for("index"))
    else:
        # kijken of gebruiker wel een recept heeft
        recipe_check = db.execute("SELECT * FROM recipes WHERE id=:id", id=id)
        if not recipe_check:
            return redirect(url_for("recipe"))
        # alle gebruikers behalve gebruiker zelf selecteren
        users = db.execute("SELECT id FROM recipes WHERE id!=:id", id=id)
        # alle gebruikers in een lijst zetten
        userlist = [int(user) for user in re.findall('\d+', str(users))]
        # gebruikers die al gematcht zijn uit lijst halen
        matches = check_matches(id)
        liked = check_liked(id)
        [userlist.remove(match) for match in matches if match in userlist]
        # accounts die in sessie al weergeven zijn eruit halen
        [userlist.remove(match) for match in session["already"] if match in userlist]
        # al gelikete accounts eruit halen:
        [userlist.remove(match) for match in liked if match in userlist]

        # als alle gebruikers al weergeven zijn moet er iets gebeuren, logt nu uit!!!!
        if userlist == []:
            return(redirect(url_for("matches")))
        # willekeurige gebruiker uitkiezen
        gerecht = []

        while gerecht == []:
            # random gebruiker selecteren
            user = random.choice(userlist)
            gerecht = db.execute("SELECT * FROM recipes WHERE id=:id", id=user)
            if user not in session["already"]:
                session["already"].append(user)
        imageid = gerecht[0]["imageid"]
        title = gerecht[0]["title"]
        bio = gerecht[0]["bio"]
        tags = [tag for tag in gerecht[0] if gerecht[0][tag]==1]
        tags = ", ".join(tags)
        if not tags:
            tags = "None"
        # likedid opslaan in globale variabele
        session["likedid"] = user
        return render_template("index.html", imageid=imageid, title=title, bio=bio, tags=tags)

@app.route("/like", methods=["GET", "POST"])
@login_required
def like():
    if request.method == "POST":
        db.execute("INSERT INTO like(currentid, likedid) VALUES(currentid=:currentid, likedid=:likedid)", currentid=session["user_id"], likedid=session["likedid"])
        return render_template("index.html")
    else:
        return render_template("index.html")

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")

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

        # create list of users that have been shown in browse
        session["already"] = []

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
    session.clear()
    if request.method == "POST":

        fromaddr = "foodiematch21@gmail.com"
        toaddr = request.form.get("email")

        msg = MIMEMultipart()

        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Registration confirmation"

        body = "Thank you for registering on FoodieMatch!\n We wish you a wonderful time on our platform! \n Hopefully you will meet awesome cooks and people. \n\n\n Kind regards, \n Team FoodieMatch"
        msg.attach(MIMEText(body, 'plain'))

        filename = "background_foodiematch.png"
        attachment = open("static/background_foodiematch.png", "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, "FoodieMatch21#")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()

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
        db.execute("INSERT INTO users(email, name, town, hash) VALUES(:email, :name, :town, :hash)", email=request.form.get("email"), name=request.form.get("name"), town=request.form.get("town"), hash=password)
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        #nu ingelogd:
        id =rows[0]["id"]
        session["user_id"] = id
        # redirect user to home page
        return redirect(url_for("logout"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    """Forgot password"""

    if request.method == "POST":

        # check if all fields are filled out
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

        # get user's info
        user = db.execute("SELECT * FROM users WHERE email = :email", \
                            email=request.form.get("email"))

        # check if email is known
        if not user:
            return apology("sorry don't know that e-mail!")

        # check if forms match with database
        if (user[0]["name"]) != request.form.get("name"):
            return("name not valid")

        elif user[0]["town"] != request.form.get("town"):
            return("town not valid")

        # if okay, update database with new password
        else:
            hash = pwd_context.hash(request.form.get("new password"))
            db.execute("UPDATE users SET hash = :hash WHERE email = :email", \
                    hash=hash, email=request.form.get("email"))
            flash("New password set!")
            return render_template("login.html")
    else:
        return render_template("forgot.html")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change your password"""
    if request.method == "POST":
        # oude wachtwoord opgeven
        if not request.form.get("current"):
            return apology("vul je huidige wachtwoord in")

        # nieuwe wachtwoord opgeven
        if not request.form.get("new"):
            return apology("vul je nieuwe wachtwoord in")

        # wachtwoord bevestigen
        elif not request.form.get("confirmation"):
            return apology("vul je bevestiging in")

        #checken of het huidige wachtwoord klopt
        rij = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
        if len(rij) != 1 or not pwd_context.verify(request.form.get("current"), rij[0]["hash"]):
            return apology("huidige wachtwoord komt niet overeen met je echte wachtwoord")

        #checken of de nieuwe hetzelfde zijn
        if request.form.get("new") != request.form.get("confirmation"):
            return apology("nieuwe wachtwoorden zijn niet gelijk aan elkaar")

        #database updaten
        db.execute("UPDATE users SET hash =:hash WHERE \
        id=:id", id=session["user_id"], hash=pwd_context.hash(request.form.get("confirmation")))

        return redirect(url_for("index"))

    else:
        return render_template("account.html")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Delete your account"""
    if request.method == "POST":

        #wachtwoord bevestigen
        if not request.form.get("old"):
            return apology("bevestig je accountverwijdering met je wachtwoord")

        #wachtwoord controleren
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])

        # ensure email exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("old"), rows[0]["hash"]):
            return apology("wachtwoord komt niet overeen met echte wachtwoord")

        else:
            #user verwijderen
            db.execute("DELETE FROM users WHERE id=:id", id=session["user_id"])

            #afbeelding van gebruiker verwijderen
            oldfile = db.execute("SELECT imageid FROM recipes WHERE id=:id", id=session["user_id"])
            os.remove(oldfile[0]["imageid"])

            #recipe verwijderen
            db.execute("DELETE FROM recipes WHERE id=:id", id=session["user_id"])

            #jouw likes verwijderen
            db.execute("DELETE FROM like WHERE currentid=:currentid", currentid=session["user_id"])

            #acties die jouw hebben geliket verwijderen
            db.execute("DELETE FROM like WHERE likedid=:likedid", likedid=session["user_id"])

            return redirect(url_for("login"))

    else:
        return render_template("account.html")

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

        # imagecheck
        report = imagereport(imageid)
        imagestatus = imagecheck(report)
        if imagestatus != True:
            os.remove(imageid)
            db.execute("DELETE FROM recipes WHERE id=:id", id=id)
            return apology(imagestatus, 200)

        # alles in de database gooien
        db.execute("INSERT INTO recipes(id, title, bio, imageid) VALUES(:id, :title, :bio, :imageid)", id=id, title=title, bio=bio, imageid=imageid)
        # update tags in database
        for tag in tags:
            db.execute("UPDATE recipes SET :tag = 1 WHERE id=:id", id=id, tag=tag)
        return redirect(url_for("index"))

    else:
        return render_template("recipe.html")

@app.route("/matches")
@login_required
def matches():
    recipelist = []
    userdata = []
    id = session["user_id"]
    matchset = check_matches(id)
    for id in matchset:
        recipe = db.execute("SELECT * FROM recipes WHERE id=:id", id=id)
        users = db.execute ("SELECT * FROM users WHERE id=:id", id=id)
        recipe[0]["email"] = users[0]["email"]
        recipe[0]["name"] = users[0]["name"]
        recipe[0]["town"] = users[0]["town"]
        recipe[0]["tags"] = [tag for tag in recipe[0] if recipe[0][tag]==1]
        if not recipe[0]["tags"]:
            recipe[0]["tags"] = "None"
        recipelist.append(recipe)
    return render_template("matches.html", recipelist=recipelist)

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
        db.execute("UPDATE recipes SET corn = NULL, egg = NULL, fish = NULL, meat = NULL, milk = NULL,	peanut = NULL, shellfish = NULL, soy = NULL, 'tree nut' = NULL, wheat = NULL, FPIES = NULL WHERE id=:id", id=id)
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
        # imagecheck
        report = imagereport(imageid)
        imagestatus = imagecheck(report)
        if imagestatus != True:
            os.remove(imageid)
            db.execute("DELETE FROM recipes WHERE id=:id", id=id)
            return apology(imagestatus, 200)

        # alles in de database gooien
        db.execute("UPDATE recipes SET title=:title, bio=:bio, imageid=:imageid WHERE id=:id", id=id, title=title, bio=bio, imageid=imageid)
        return redirect(url_for("index"))

    else:
        huidig = db.execute("SELECT * FROM recipes WHERE id=:id", id=session["user_id"])
        if not huidig:
            return redirect(url_for("recipe"))
        else:
            tags = [tag for tag in huidig[0] if huidig[0][tag]==1]
            tags = ", ".join(tags)
            if not tags:
                tags = "None"
            return render_template("changerecipe.html", huidig=huidig, tags=tags)


