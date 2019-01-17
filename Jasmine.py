import csv
import urllib.request
import smtplib

from cs50 import SQL
from flask import redirect, render_template, request, session, url_for

from functools import wraps
from .forms import EmailForm, PasswordForm
from .models import User
from .util import send_email, ts

def send_email(user,email,subject,html):
    """Send user mail"""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("foodiematch21@gmail.com", "FoodieMatch21#")
    sever.sendmail("foodiematch21@gmail.com", email, message)

@app.route('/reset', methods=["GET", "POST"])
def reset():
    """Reset password function"""

    form = EmailForm()
    if form.validate_on_submit()
        user = User.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"

        # Here we use the URLSafeTimedSerializer we created in `util` at the
        # beginning of the chapter
        token = ts.dumps(self.email, salt='recover-key')

        recover_url = url_for(
            'reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'email/recover.html',
            recover_url=recover_url)

        # Let's assume that send_email was defined in myapp/util.py
        send_email(user.email, subject, html)

        return redirect(url_for('index'))
    return render_template('reset.html', form=form)

    @app.route('/reset/<token>', methods=["GET", "POST"])
    def reset_token(token):
        """Reset password with token"""

        try:
            email = ts.loads(token, salt="recovery-key", max_age=86400)
        except:
            abort(404)

            form = PasswordForm()

            if form.validate_on_submit():
                user = User.query.filter_by(email=email).first_or_404()

                user.password = form.password.data

                db.session.add(user)
                db.session.commit()

                return redirect(url_for('login'))
            return render_template('reset_token.html', form=form, token=token)