#Mike van Gils - 12363197

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

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
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///foodiematch.db")

@app.route("/")
@login_required
def index():
    #alle aandelen met aantallen
    dingetjes = db.execute("SELECT symbol, shares \
    FROM portfolio WHERE id=:id", id=session["user_id"])

    alles = 0

    #voor elk aandeel in alle portfolio aandelen
    for ding in dingetjes:
        symbol = ding["symbol"]
        shares = ding["shares"]
        current_price = lookup(symbol)
        current_price = current_price["price"]
        total_price = shares * current_price
        alles += total_price
        #nieuwste prijs wordt toegevoegd om hem vervolgens zometeen weer terug te halen naar .html
        db.execute("UPDATE portfolio SET price=:price, \
        total_price=:total_price WHERE id=:id AND symbol=:symbol",
        price=usd(current_price),
        total_price=usd(total_price), id=session["user_id"], symbol=symbol)

    #hoeveelheid besteedbaar geld
    cash_niveau = db.execute("SELECT cash FROM users WHERE id=:id",
    id=session["user_id"])

    #geld+waarde aandelen
    portefeuille_waarde = alles + cash_niveau[0]["cash"]

    #alle aandelen
    resultaten = db.execute("SELECT * FROM portfolio \
    WHERE id=:id", id=session["user_id"])

    #stuur de aandelen, cash en portefeuille waarde mee
    return render_template("browse.html", resultaten=resultaten,
    cash_niveau=cash_niveau[0]["cash"], portefeuille_waarde=portefeuille_waarde)

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
        return redirect(url_for(""))

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
        return redirect(url_for(""))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")