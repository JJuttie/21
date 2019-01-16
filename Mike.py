import csv
import urllib.request
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps

def register2():
    """Register user."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

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

        # pomp het in de database
        gebruiker = db.execute("INSERT INTO users(email, name, town, hash) VALUES(:email, :name, :town, :hash)",
        email=request.form.get("email"), name=request.form.get("name"),
        town=request.form.get("town"), hash=password)

        #email al in gebruik
        if not gebruiker:
            return apology("eMail has already been used")

        #nu ingelogd:
        session["user-id"] = gebruiker
        # redirect user to home page
        return redirect(url_for("recipe"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
