from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.__all_models import User, Product, Category, News
from forms.__all_forms import RegisterForm, LoginForm, GamesForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import shutil
import os
from resources import user_resource, product_resource
from flask_restful import reqparse, abort, Api, Resource
from requests import get, post, delete, put


db_session.global_init("db/shop.db")
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_sess = db_session.create_session()
login_manager = LoginManager()
login_manager.init_app(app)
db_session.expire_on_commit = False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def main():
    db_sess = db_session.create_session()
    message = ''
    games = db_sess.query(Product).all()
    empty = True
    if len(games) > 0:
        empty = False
    if not empty:
        pr = []
        res = []
        for i in games:
            pr.append(i)
            if len(pr) == 4:
                res.append(pr)
                pr = []
        if len(pr) != 0:
            res.append(pr)

    news = db_sess.query(News).filter(News.is_published).all()
    empty2 = True
    if len(news) > 0:
        empty2 = False
    if not empty2:
        pr = []
        res2 = []
        for i in news:
            pr.append(i)
            if len(pr) == 2:
                res2.append(pr)
                pr = []
        if len(pr) != 0:
            res2.append(pr)

    if request.method == 'POST':
        search = None
        for game in games:
            if game.title.lower() == request.form['search'].lower():
                search = game
                break
        if search is not None:
            return redirect(f'/games_info/{search.id}')
        else:
            message = 'Ничего не найдено'
    return render_template("index.html", games=res, empty=empty, genres=db_sess.query(Category).all(),
                           message=message, empty2=empty2, news=res2)


@app.route('/search/<criteria>', methods=['GET', 'POST'])
def search(criteria):
    message = ''
    db_sess = db_session.create_session()
    cat = db_sess.query(Category).filter(Category.name == criteria).first()
    games = db_sess.query(Product).all()
    res = []
    for game in games:
        if cat in game.categories:
            res.append(game)
    empty = False
    if len(res) == 0:
        empty = True
    if request.method == 'POST':
        search = None
        for game in games:
            if game.title.lower() == request.form['search'].lower():
                search = game
                break
        if search is not None:
            return redirect(f'/games_info/{search.id}')
        else:
            message = 'Ничего не найдено'
    return render_template('index.html', games=res, empty=empty, genres=db_sess.query(Category).all(), message=message,)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        res = post('http://127.0.0.1:8080/api/user',
                   json={'name': form.name.data, 'email': form.email.data, 'role': 'user',
                         'password': form.password.data
                         })
        if not res:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с такой почтой уже есть")
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/games', methods=['GET', 'POST'])
@login_required
def add_games():
    form = GamesForm()
    if form.validate_on_submit():
        res = post('http://127.0.0.1:8080/api/product',
                    json={'title': form.title.data, 'description': form.description.data, 'picture': form.picture.data.filename,
                         'developer': form.developer.data, 'publisher': form.publisher.data, 'date': form.date.data,
                         'price': form.price.data, 'quantity': form.quantity.data, 'genres': form.genres.data
                         })
        out = open(f'{form.picture.data.filename}', "wb")
        out.write(form.picture.data.read())
        out.close()
        shutil.move(f'{form.picture.data.filename}', f'static/img/{form.picture.data.filename}')
        return redirect('/')
    return render_template('games.html', form=form)


@app.route('/games_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_games(id):
    form = GamesForm()
    if request.method == "GET":
        res = get(f'http://127.0.0.1:8080/api/product/{id}')
        if res:
            res = res.json()['product']
            form.title.data = res['title']
            form.description.data = res['description']
            form.picture.data = res['picture']
            form.developer.data = res['developer']
            form.publisher.data = res['publisher']
            form.genres.data = res['genres']
            form.date.data = res['date']
            form.price.data = res['price']
            form.quantity.data = res['quantity']
        else:
            abort(404)
    if form.validate_on_submit():
        res = put(f'http://127.0.0.1:8080/api/product/{id}',
                   json={'title': form.title.data, 'description': form.description.data, 'picture': form.picture.data.filename,
                         'developer': form.developer.data, 'publisher': form.publisher.data, 'date': form.date.data,
                         'price': form.price.data, 'quantity': form.quantity.data, 'genres': form.genres.data
                         })
        if res:
            out = open(f'{form.picture.data.filename}', "wb")
            out.write(form.picture.data.read())
            out.close()
            shutil.move(f'{form.picture.data.filename}', f'static/img/{form.picture.data.filename}')
            return redirect('/')
        else:
            abort(404)
    return render_template('games.html', form=form)


@app.route('/games_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def games_delete(id):
    res = delete(f'http://127.0.0.1:8080/api/product/{id}')
    if res:
        return redirect('/')
    else:
        abort(404)


@app.route('/games_info/<int:id>')
def games_info(id):
    db_sess = db_session.create_session()
    games = db_sess.query(Product).filter(Product.id == id).first()
    if not games:
        abort(404)
    check = False
    if current_user.is_authenticated:
        for i in current_user.cart:
            if i.id == id:
                check = True
    return render_template('games_info.html', item=games, check=check)


@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    games = db_sess.query(Product).filter(Product.id == id).first()
    if games:
        user.cart.append(games)
        games.quantity -= 1
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/games_info/{id}')


@app.route('/cart')
def cart():
    empty = True
    if len(current_user.cart) > 0:
        empty = False
    return render_template('cart.html', empty=empty)


@app.route('/cart_delete/<int:id>')
def cart_delete(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    games = db_sess.query(Product).filter(Product.id == id).first()
    if games:
        user.cart.remove(games)
        games.quantity += 1
        db_sess.commit()
    else:
        abort(404)
    return redirect('/cart')


@app.route('/order')
def order():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    for i in user.cart:
        user.cart.remove(i)
        db_sess.commit()
    return redirect('/')


@app.route('/news_info/<int:id>')
def news_info(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if not news:
        abort(404)
    return render_template('news_info.html', item=news)


if __name__ == '__main__':
    api.add_resource(user_resource.UserListResource, '/api/user')
    api.add_resource(user_resource.UserResource, '/api/user/<int:product_id>')
    api.add_resource(product_resource.ProductListResource, '/api/product')
    api.add_resource(product_resource.ProductResource, '/api/product/<int:product_id>')

    """
    db_sess = db_session.create_session()
    news = News(title="Новость_1", content="Контент\nКонтент",
                user_id=1, picture='img_3.jpg', is_published=True)
    db_sess.add(news)
    db_sess.commit()
    """

    app.run(port=8080, host='127.0.0.1', debug=True)
