from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *
from Mike import *
from Jasmine import *
from Alex import *
from Sebas import *

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
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    return apology("")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

        # username opgeven
        if not request.form.get("username"):
            return apology("must provide username")

        # wachtwoord opgeven
        elif not request.form.get("password"):
            return apology("must provide password")

        # wachtwoord bevestigen
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password")

        # checken
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("wachtwoorden zijn niet gelijk aan elkaar")

        #wachtwoord encrypten
        password=pwd_context.hash(request.form.get("password"))

        # pomp het in de database
        gebruiker = db.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)",
        username=request.form.get("username"), hash=password)

        #gebruikersnaampie al in gebruik
        if not gebruiker:
            return apology("Username is al bezet")

        #nu ingelogd:
        session["user-id"] = gebruiker
        # redirect user to home page
        return redirect(url_for("index"))

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
recipe()