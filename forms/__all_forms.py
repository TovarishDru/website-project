from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField, IntegerField, FileField, \
    SelectMultipleField
from wtforms import DateField
from wtforms.validators import DataRequired, ValidationError
from wtforms.fields.html5 import EmailField
# from wtforms.fields.html5 import EmailField, DateField
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.widgets import CheckboxInput, ListWidget


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


class NonValidatingSelectField(SelectMultipleField):
    def pre_validate(self, form):
        pass


class GamesForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField("Описание")
    picture = FileField('Изображение', validators=[FileRequired()])
    developer = StringField('Разработчик')
    publisher = StringField('Издатель')
    genres = NonValidatingSelectField(
        'Жанры',
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=True))
    date = IntegerField('Дата выхода')
    price = IntegerField('Цена')
    quantity = IntegerField('Количество ключей')
    submit = SubmitField('Применить')


class NewsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Контент")
    picture = FileField('Изображение', validators=[FileRequired()])
    submit = SubmitField('Применить')


def cvv_check(form, field):
    if len(field.data) != 3:
        raise ValidationError('Введите корректный cvv')
    elif not all(list(map(lambda x: x.isdigit(), list(field.data)))):
        raise ValidationError('Введите корректный cvv')


def number_check(form, field):
    if len(field.data) not in (13, 16, 19):
        raise ValidationError('Введите корректный номер карты')
    elif not all(list(map(lambda x: x.isdigit(), list(field.data)))):
        raise ValidationError('Введите корректный номер карты')


def date_check(form, field):
    try:
        a = field.data.split('/')
        if int(a[0]) not in range(1, 13):
            raise Exception()
        elif len(a[1]) != 4 or not all(list(map(lambda x: x.isdigit(), list(a[1])))):
            raise Exception()
    except Exception:
        raise ValidationError('Введите корректную дату')


class OrderForm(FlaskForm):
    number = StringField('Номер карты', validators=[DataRequired(), number_check])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    code = StringField('CVV', validators=[DataRequired(), cvv_check])
    date = StringField("Действует до (мм/гггг)", validators=[DataRequired(), date_check])
    submit = SubmitField('Заказать')

