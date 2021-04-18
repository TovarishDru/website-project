from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.__all_models import User, Product, Category, News
from forms.__all_forms import RegisterForm, LoginForm, GamesForm, NewsForm, OrderForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import shutil
import os
from resources import user_resource, product_resource
from resources.product_search import product_search
from flask_restful import reqparse, abort, Api, Resource
from requests import get, post, delete, put
import datetime

db_session.global_init("db/shop.db")
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db_sess = db_session.create_session()
login_manager = LoginManager()
login_manager.init_app(app)
db_session.expire_on_commit = False


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


def generate_img_name(type, file):
    if '.' in file:
        ext = file.split('.')[-1]
    else:
        ext = 'png'
    files = os.listdir('static/img')
    files = list(filter(lambda x: x.startswith(type), files))
    if files:
        files = list(map(lambda x: int(x.split('.')[0][len(type) + 1:]), files))
        ind = max(files) + 1
    else:
        ind = 1
    filename = f'{type}_{ind}.{ext}'
    return filename


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def main():
    db_sess = db_session.create_session()
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
        return redirect(f"/search/request={request.form['search'].lower()}")
    return render_template("index.html", games=res, empty=empty, genres=db_sess.query(Category).all(),
                           empty2=empty2, news=res2, year=datetime.date.today().year)


@app.route('/search/request=<search_request>', methods=['GET', 'POST'])
def search_games(search_request):
    if request.method == 'POST':
        return redirect(f"/search/request={request.form['search'].lower()}")
    res = product_search(search_request)
    session = db_session.create_session()
    games = []
    for id in res:
        games.append(session.query(Product).get(id))
    pr = []
    res = []
    for i in games:
        pr.append(i)
        if len(pr) == 4:
            res.append(pr)
            pr = []
    if len(pr) != 0:
        res.append(pr)
    return render_template('search_games.html', games=res, request=search_request, empty=not bool(res),
                           genres=db_sess.query(Category).all(),
                           year=datetime.date.today().year)


@app.route('/search/category=<criteria>', methods=['GET', 'POST'])
def search_category(criteria):
    db_sess = db_session.create_session()
    cat = db_sess.query(Category).filter(Category.name == criteria).first()
    games = db_sess.query(Product).all()
    res = []
    for game in games:
        if cat in game.categories:
            res.append(game)
    games = res[:]
    pr = []
    res = []
    for i in games:
        pr.append(i)
        if len(pr) == 4:
            res.append(pr)
            pr = []
    if len(pr) != 0:
        res.append(pr)
    print(res)
    if request.method == 'POST':
        return redirect(f"/search/request={request.form['search'].lower()}")
    return render_template('search_category.html', games=res, empty=not bool(games), category=criteria,
                           genres=db_sess.query(Category).all(),
                           year=datetime.date.today().year)


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
    db_sess = db_session.create_session()
    genres = db_sess.query(Category).all()
    form.genres.choices = [(genre.id, genre.name) for genre in genres]
    if form.validate_on_submit():
        filename = generate_img_name('products', form.picture.data.filename)
        res = post('http://127.0.0.1:8080/api/product',
                   json={'title': form.title.data, 'description': form.description.data,
                         'picture': filename,
                         'developer': form.developer.data, 'publisher': form.publisher.data, 'date': form.date.data,
                         'price': form.price.data, 'quantity': form.quantity.data, 'genres': ','.join(form.genres.data)
                         })
        out = open(f'{filename}', "wb")
        out.write(form.picture.data.read())
        out.close()
        shutil.move(f'{filename}', f'static/img/{filename}')
        return redirect('/')
    return render_template('games.html', form=form, title='Добавление игры')


@app.route('/games_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_games(id):
    form = GamesForm()
    db_sess = db_session.create_session()
    genres = db_sess.query(Category).all()
    form.genres.choices = [(genre.id, genre.name) for genre in genres]
    if request.method == "GET":
        res = get(f'http://127.0.0.1:8080/api/product/{id}')
        if res:
            res = res.json()['product']
            form.title.data = res['title']
            form.description.data = res['description']
            form.picture.data = res['picture']
            form.developer.data = res['developer']
            form.publisher.data = res['publisher']
            # form.genres.data = res['genres']
            form.date.data = res['date']
            form.price.data = res['price']
            form.quantity.data = res['quantity']
        else:
            abort(404)
    if form.validate_on_submit():
        res = get(f'http://127.0.0.1:8080/api/product/{id}').json()['product']
        try:
            os.remove(f"static/img/{res['picture']}")
        except Exception:
            pass

        filename = generate_img_name('products', form.picture.data.filename)
        res = put(f'http://127.0.0.1:8080/api/product/{id}',
                  json={'title': form.title.data, 'description': form.description.data,
                        'picture': filename,
                        'developer': form.developer.data, 'publisher': form.publisher.data, 'date': form.date.data,
                        'price': form.price.data, 'quantity': form.quantity.data, 'genres': ','.join(form.genres.data)
                        })
        if res:
            out = open(f'{filename}', "wb")
            out.write(form.picture.data.read())
            out.close()
            shutil.move(f'{filename}', f'static/img/{filename}')
            return redirect('/')
        else:
            abort(404)
    return render_template('games.html', form=form, title='Редактирование игры')


@app.route('/games_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def games_delete(id):
    res = delete(f'http://127.0.0.1:8080/api/product/{id}')
    if res:
        return redirect('/')
    else:
        abort(404)


@app.route('/games_info/<int:id>', methods=['GET', 'POST'])
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
    if request.method == 'POST':
        return redirect(f"/search/request={request.form['search'].lower()}")
    return render_template('games_info.html', item=games, check=check, genres=db_sess.query(Category).all(),
                           year=datetime.date.today().year)


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


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    empty = True
    if len(current_user.cart) > 0:
        empty = False
    games = current_user.cart
    for game in games:
        a = game.categories
    if request.method == 'POST':
        return redirect(f"/search/request={request.form['search'].lower()}")
    return render_template('cart.html', empty=empty, cart=games, genres=db_sess.query(Category).all(),
                           year=datetime.date.today().year)


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


@app.route('/order', methods=['GET', 'POST'])
def order():
    form = OrderForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.cart.clear()
        db_sess.commit()
        return redirect('/after_order')

    return render_template('order.html', form=form)


@app.route('/after_order', methods=['GET', 'POST'])
def after_order():
    if request.method == 'POST':
        return redirect(f"/search/request={request.form['search'].lower()}")
    return render_template('after_order.html', genres=db_sess.query(Category).all(), year=datetime.date.today().year)


@app.route('/news_info/<int:id>', methods=['GET', 'POST'])
def news_info(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if not news:
        abort(404)
    if request.method == 'POST':
        return redirect(f"/search/request={request.form['search'].lower()}")
    return render_template('news_info.html', item=news, genres=db_sess.query(Category).all(),
                           year=datetime.date.today().year)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    is_published = True
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role == 'user':
        is_published = False
    form = NewsForm()
    if form.validate_on_submit():
        filename = generate_img_name('news', form.picture.data.filename)
        db_sess = db_session.create_session()
        news = News(title=form.title.data, content=form.content.data,
                    user_id=current_user.id, picture=filename, is_published=is_published)
        db_sess.add(news)
        db_sess.commit()
        out = open(f'{filename}', "wb")
        out.write(form.picture.data.read())
        out.close()
        shutil.move(f'{filename}', f'static/img/{filename}')
        return redirect('/')
    return render_template('news.html', form=form, title='Добавление новсти')


@app.route('/news_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    if not current_user.is_authenticated:
        abort(404)
    if current_user.role != 'admin':
        abort(404)
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).get(id)
        if not news:
            abort(404)
        form.title.data = news.title
        form.content.data = news.content
        form.picture.data = news.picture
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).get(id)
        if not news:
            abort(404)
        news.title = form.title.data
        news.content = form.content.data
        try:
            os.remove(f"static/img/{news.picture}")
        except Exception:
            pass
        filename = generate_img_name('news', form.picture.data.filename)
        news.picture = filename
        out = open(f'{filename}', "wb")
        out.write(form.picture.data.read())
        out.close()
        shutil.move(f'{filename}', f'static/img/{filename}')
        session.commit()
        return redirect('/')
    return render_template('news.html', form=form, title='Редактирование новости')


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).get(id)
    if not news:
        abort(404, message=f"News {id} not found")
    news = session.query(News).get(id)
    try:
        os.remove(f'static/img/{news.picture}')
    except Exception:
        pass
    session.delete(news)
    session.commit()
    return redirect('/')


@app.route('/news_list', methods=['GET', 'POST'])
@login_required
def news_list():
    if not current_user.is_authenticated or not current_user.role == 'admin':
        abort(404)
    session = db_session.create_session()
    news = session.query(News).filter(News.is_published == 0).all()
    res = []
    if len(news) > 0:
        pr = []
        res = []
        for i in news:
            pr.append(i)
            if len(pr) == 2:
                res.append(pr)
                pr = []
        if len(pr) != 0:
            res.append(pr)
    return render_template('news_list.html', news=res)


@app.route('/news_info_admin/<int:id>')
@login_required
def news_info_admin(id):
    if not current_user.is_authenticated or not current_user.role == 'admin':
        abort(404)
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if not news or news.is_published:
        abort(404)
    if not news:
        abort(404)
    return render_template('news_info_admin.html', item=news)


@app.route('/news_accept/<int:id>')
@login_required
def news_accept(id):
    if not current_user.is_authenticated or not current_user.role == 'admin':
        abort(404)
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if not news:
        abort(404)
    news.is_published = True
    db_sess.commit()
    return redirect('/news_list')


@app.route('/news_reject/<int:id>')
@login_required
def news_reject(id):
    if not current_user.is_authenticated or not current_user.role == 'admin':
        abort(404)
    session = db_session.create_session()
    news = session.query(News).get(id)
    if not news:
        abort(404)
    os.remove(f'static/img/{news.picture}')
    session.delete(news)
    session.commit()
    return redirect('/news_list')


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
