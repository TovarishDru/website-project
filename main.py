from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.__all_models import User, Product, Category
from forms.__all_forms import RegisterForm, LoginForm, GamesForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import shutil
import os


db_session.global_init("db/shop.db")
app = Flask(__name__)
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
      return render_template("index.html", games=games, empty=empty, genres=db_sess.query(Category).all(), message=message)


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
      return render_template('index.html', games=res, empty=empty, genres=db_sess.query(Category).all(), message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
      form = RegisterForm()
      if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                  return render_template('register.html', title='Регистрация',
                                    form=form,
                                    message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                  return render_template('register.html', title='Регистрация',
                                    form=form,
                                    message="Такой пользователь уже есть")
            user = User(
                  name=form.name.data,
                  email=form.email.data,
                  role='user'
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
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


@app.route('/games',  methods=['GET', 'POST'])
@login_required
def add_games():
      form = GamesForm()
      if form.validate_on_submit():
            db_sess = db_session.create_session()
            games = Product()
            games.title = form.title.data
            games.description = form.description.data
            games.picture = form.picture.data.filename
            out = open(f'{form.picture.data.filename}', "wb")
            out.write(form.picture.data.read())
            out.close()
            shutil.move(f'{form.picture.data.filename}', f'static/img/{form.picture.data.filename}')
            games.developer = form.developer.data
            games.publisher = form.publisher.data
            for i in form.genres.data.split(','):
                  cat = db_sess.query(Category).filter(Category.name == i).first()
                  if cat is not None:
                        games.categories.append(cat)
            games.date = form.date.data
            games.price = form.price.data
            games.quantity = form.quantity.data
            db_sess.add(games)
            db_sess.commit()
            return redirect('/')
      return render_template('games.html', form=form)


@app.route('/games_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_games(id):
      form = GamesForm()
      if request.method == "GET":
            db_sess = db_session.create_session()
            games = db_sess.query(Product).filter(Product.id == id).first()
            if games:
                  form.title.data = games.title
                  form.description.data = games.description
                  form.picture.data = games.picture
                  form.developer.data = games.developer
                  form.publisher.data = games.publisher
                  cat = ''
                  for i in games.categories:
                        cat += i.name + ','
                  form.genres.data = cat[:-1]
                  form.date.data = games.date
                  form.price.data = games.price
                  form.quantity.data = games.quantity
            else:
                  abort(404)
      if form.validate_on_submit():
            db_sess = db_session.create_session()
            games = db_sess.query(Product).filter(Product.id == id).first()
            if games:
                  games.title = form.title.data
                  games.description = form.description.data
                  games.picture = form.picture.data.filename
                  out = open(f'{form.picture.data.filename}', "wb")
                  out.write(form.picture.data.read())
                  out.close()
                  shutil.move(f'{form.picture.data.filename}', f'static/img/{form.picture.data.filename}')
                  games.developer = form.developer.data
                  games.publisher = form.publisher.data
                  for i in games.categories:
                        games.categories.remove(i)
                  for i in form.genres.data.split(','):
                        cat = db_sess.query(Category).filter(Category.name == i).first()
                        if cat is not None:
                              games.categories.append(cat)
                  games.date = form.date.data
                  games.price = form.price.data
                  games.quantity = form.quantity.data
                  db_sess.commit()
                  return redirect('/')
            else:
                  abort(404)
      return render_template('games.html', form=form)


@app.route('/games_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def games_delete(id):
      db_sess = db_session.create_session()
      games = db_sess.query(Product).filter(Product.id == id).first()
      if games:
            os.remove(f'static/img/{games.picture}')
            db_sess.delete(games)
            db_sess.commit()
      else:
            abort(404)
      return redirect('/')


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


if __name__ == '__main__':
      app.run(port=8080, host='127.0.0.1', debug=True)