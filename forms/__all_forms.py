from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class GamesForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField("Описание")
    picture = FileField('Изображение', validators=[FileRequired()])
    developer = StringField('Разработчик')
    publisher = StringField('Издатель')
    genres = TextAreaField('Жанры (через запятую без пробелов)')
    date = IntegerField('Дата выхода')
    price = IntegerField('Цена')
    quantity = IntegerField('Количество ключей')
    submit = SubmitField('Применить')


class NewsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Контент")
    picture = FileField('Изображение', validators=[FileRequired()])
    submit = SubmitField('Добавить')