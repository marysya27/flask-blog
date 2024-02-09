from flask_wtf import FlaskForm
from wtforms.validators import Email, DataRequired, Length, EqualTo
from wtforms import StringField, PasswordField, BooleanField, SubmitField

class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[Email()])
    psw = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=100)])
    remember = BooleanField('Remember me', default=False)
    submit = SubmitField('Enter')

class RegisterForm(FlaskForm):
    name = StringField('Name: ', validators=[Length(min=4, max=100)])
    email = StringField('Email: ', validators=[Email()])
    psw = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=100)])

    psw2 = PasswordField('Password again: ', validators=[DataRequired(), EqualTo('psw')])
    submit = SubmitField('Register')




