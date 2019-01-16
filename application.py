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

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "POST":
        #vakjes contorleren
        if not request.form.get("symbol"):
            return apology("Geen aandeel ingevuld")
        elif not request.form.get("shares"):
            return apology("Geen aantal ingevuld")
        elif not request.form.get("shares").isdigit():
            return apology("Ongeldig aantal ingevuld")

        #aantal controleren
        aantal = int(request.form.get("shares"))
        if aantal < 0:
            return apology("ongeldig aantal")

        #check of het aandeel bestaat
        aandeel_info=lookup(request.form.get("symbol"))
        if not aandeel_info:
            return apology("Onbekend aandeel")

        #het cashniveau
        geld = db.execute("SELECT cash FROM users WHERE id =:id", id=session["user_id"])
        geld = geld[0]["cash"]
        #totaalprijs
        price = aandeel_info["price"] * aantal
        #als je niet genoeg geld hebt
        if geld < price:
            return apology("Niet genoeg geld.")
        #nieuw cashniveau
        nieuw_geld = geld - price

        #rekening afschrijven
        db.execute("UPDATE users SET cash =:nieuw_geld WHERE id=:id", nieuw_geld=nieuw_geld, id=session["user_id"])

        #toevoegen aan history (history zijn alle transacties)
        db.execute("INSERT INTO history(id, bought_sold, symbol, shares, price) VALUES(:id, :bought_sold, :symbol, :shares, :price)",
        id=session["user_id"], bought_sold="BOUGHT", symbol=request.form.get("symbol"),
        shares=aantal, price=usd(aandeel_info["price"]))

        #toevoegen aan portfolio als hij al dit aandeel had (portfolio is overzicht per klant, totaalbedrag per aandeel)
        #aantaal aandelen wat hij al had van dit symbol
        al_gekocht = db.execute("SELECT shares FROM portfolio \
        WHERE id=:id AND symbol =:symbol",
        id=session["user_id"], symbol=aandeel_info["symbol"])

        #hij had nog geen aandelen van dit symbol:
        if not al_gekocht:
            db.execute("INSERT INTO portfolio(id, symbol, shares, price, total_price)\
            VALUES(:id, :symbol, :shares, :price, :total_price)",
            id=session["user_id"], symbol=aandeel_info["symbol"],
            shares=aantal, price=usd(aandeel_info["price"]),
            total_price=price)
        else:
            #eerder gekocht dus aantal shares updaten
            totaal_aantal = al_gekocht[0]["shares"] + aantal
            db.execute("UPDATE portfolio SET shares=:shares\
            WHERE id=:id AND symbol=:symbol",
            shares=totaal_aantal, id=session["user_id"],
            symbol=aandeel_info["symbol"])

        return redirect(url_for("browse"))

    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    #alle transacties erbij halen
    acties = db.execute("SELECT * FROM history WHERE id=:id",
    id=session["user_id"])

    return render_template("history.html", acties=acties)

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

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        #info opzoeken
        aandeel_info = lookup(request.form.get("symbol"))
        #als het aandeel niet bestaat
        if not aandeel_info:
            return apology("Aandeel onbekend")
        #aandeelinfo meesturen
        return render_template("quoted.html", aandeel_info=aandeel_info)

    else:
        return render_template("quote.html")

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

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "POST":
        #forms contorleren
        if not request.form.get("symbol"):
            return apology("Geen aandeel ingevuld")
        elif not request.form.get("shares"):
            return apology("Geen aantal ingevuld")
        elif not request.form.get("shares").isdigit():
            return apology("Ongeldig aantal ingevuld")

        #aandeel controleren op bestaan
        aandeel_info = lookup(request.form.get("symbol"))
        if not aandeel_info:
            return apology("Onbekend aandeel")

        #aantal verkoopshares controleren
        shares = int(request.form.get("shares"))
        if shares < 1:
            return apology("Minimaal 1 verkopen!")
        #de huidige aandelen ophalen
        aandelen = db.execute("SELECT shares FROM portfolio \
        WHERE id=:id AND symbol=:symbol", id=session["user_id"],
        symbol=request.form.get("symbol"))

        #heb je uberhaubt aandelen?
        if not aandelen:
            return apology("Je hebt geen aandelen om te verkopen")
        #heb je genoeg aandelen?
        if shares > int(aandelen[0]["shares"]):
            return apology("Zoveel aandelen heb je niet van dit symbol!")

        #toevoegen aan history, later bought_sold toegevoegd om bij history.html makkelijk te tonen of het is gekocht of verkocht.
        db.execute("INSERT INTO history(id, bought_sold, symbol, shares, price) \
        VALUES(:id, :bought_sold, :symbol, :shares, :price)", id=session["user_id"], bought_sold="SOLD",
        symbol=request.form.get("symbol"), shares=shares, price=usd(aandeel_info["price"]))

        #cash updaten
        db.execute("UPDATE users SET cash = cash + :verkoopprijs WHERE \
        id=:id", id=session["user_id"], verkoopprijs=aandeel_info["price"]*float(shares))

        #aantal shares updaten
        nieuw_shares = aandelen[0]["shares"] - shares
        #wanneer alles shares nu op zijn
        if nieuw_shares < 1:
            db.execute("DELETE FROM portfolio WHERE id=:id AND symbol=:symbol",
            id=session["user_id"], symbol=request.form.get("symbol"))
        #als er nog sharesover zijn
        else:
            db.execute("UPDATE portfolio SET shares=:shares \
            WHERE id=:id AND symbol=:symbol", shares=nieuw_shares,
            id=session["user_id"], symbol=request.form.get("symbol"))

        return redirect(url_for(""))

    else:
        #keuzelijst meegeven voor de select op sell.html
        keuzelijst = db.execute("SELECT symbol FROM portfolio WHERE id=:id",
        id=session["user_id"])
        return render_template("sell.html", keuzelijst=keuzelijst)

#extra_opdracht
@app.route("/money", methods=["GET", "POST"])
@login_required
def money():
    """Add money to your account"""
    if request.method == "POST":
        try:
            money = int(request.form.get("money"))
            if money < 100:
                return("Minimaal 100, kom op het is gratis.")

        except:
            return apology("Vul een getal in")

        db.execute("UPDATE users SET cash = cash + :money WHERE \
        id=:id", money=money, id=session["user_id"])

        return redirect(url_for(""))

    else:
        return render_template("money.html")

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

        return redirect(url_for(""))

    else:
        return render_template("password.html")