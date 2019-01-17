from flask_wtf import Form
from wtforms import SpringField, PasswordField
from wtforms.validators import DataRequired, Email

class EmailForm(Form):
    email = TextField('Email', validators=[DataRequired(), Email()])

class PasswordForm(Form):
    password = PasswordField('Email', validators=[DataRequired()])