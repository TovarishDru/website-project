import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
    role = sqlalchemy.Column(sqlalchemy.String)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    cart = orm.relation("Product",
                secondary="order",
                backref="users")


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    picture = sqlalchemy.Column(sqlalchemy.String)
    developer = sqlalchemy.Column(sqlalchemy.String)
    publisher = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    quantity = sqlalchemy.Column(sqlalchemy.Integer)
    categories = orm.relation("Category",
                        secondary="association",
                        backref="products")
    association_table = sqlalchemy.Table('order', SqlAlchemyBase.metadata,
        sqlalchemy.Column('users', sqlalchemy.Integer,
                        sqlalchemy.ForeignKey('users.id')),
        sqlalchemy.Column('products', sqlalchemy.Integer,
                        sqlalchemy.ForeignKey('products.id'))
    )


class Category(SqlAlchemyBase):
    __tablename__ = 'category'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, 
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
        sqlalchemy.Column('products', sqlalchemy.Integer,
                        sqlalchemy.ForeignKey('products.id')),
        sqlalchemy.Column('category', sqlalchemy.Integer,
                        sqlalchemy.ForeignKey('category.id'))
    )