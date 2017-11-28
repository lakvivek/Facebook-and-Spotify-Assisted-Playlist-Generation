from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired("Please enter the username")])
    password = PasswordField('Passsword', validators=[DataRequired("Please enter the password")])
    submit = SubmitField('Login')