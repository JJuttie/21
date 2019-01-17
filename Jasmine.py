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

        elif not request.form.get("confirm password"):
            return apology("please confirm new password")

        elif request.form.get("new password") != request.form.get("confirmation"):
            return apology("passwords don't match")

        email = db.execute("SELECT email FROM users WHERE email =: email", \
                            email=request.form.get("email"))
        name = db.execute("SELECT name FROM users WHERE name =: name", \
                            name=request.form.get("name"))
        town = db.execute("SELECT town FROM users WHERE town =:town", \
                            town=request.form.get("town"))
        print("EMAIL", email)
        print("NAME", name)
        print("TOWN", town)

        if not email:
            return apology("not valid")
        elif not name:
            return apology("not valid")
        elif not town:
            return apology("not valid")
        else:
            new_password = pwd_context.hash(request.form.get("new password"))
            db.execute("UPDATE users SET password = :new_password WHERE id = :id", \
                    password=new_password, email=email)
            flash("New password set!")
            return render_template("login.html")
    else:
        return render_template("login.html")