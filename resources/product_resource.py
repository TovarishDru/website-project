from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.__all_models import Product, Category
from resources.product_parser import parser

import os


def abort_if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        abort(404, message=f"Product {product_id} not found")


class ProductResource(Resource):
    def get(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        cat = ''
        for i in product.categories:
            cat += i.name + ','
        res = product.to_dict(
            only=('id', 'title', 'description', 'picture', 'developer', 'publisher', 'date', 'price', 'quantity'))
        res['genres'] = cat[:-1]
        return jsonify({'product': res})

    def delete(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        try:
            os.remove(f'static/img/{product.picture}')
        except Exception:
            pass
        session.delete(product)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, product_id):
        abort_if_product_not_found(product_id)
        args = parser.parse_args()
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        product.title = args['title']
        product.description = args['description']
        product.picture = args['picture']
        product.developer = args['developer']
        product.publisher = args['publisher']
        product.date = args['date']
        product.price = args['price']
        product.quantity = args['quantity']
        for i in product.categories:
            product.categories.remove(i)
        if args['genres']:
            for i in args['genres'].split(','):
                cat = session.query(Category).filter(Category.name == i).first()
                if cat is not None:
                    product.categories.append(cat)
        session.commit()
        return jsonify({'success': 'OK'})


class ProductListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Product).all()
        ans = []
        for product in products:
            cat = ''
            for i in product.categories:
                cat += i.name + ','
            res = product.to_dict(
                only=('id', 'title', 'description', 'picture', 'developer', 'publisher', 'date', 'price', 'quantity'))
            res['genres'] = cat[:-1]
            ans.append(res)
        return jsonify({'product': ans})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Product(
            title=args['title'], description=args['description'], picture=args['picture'], developer=args['developer'],
            publisher=args['publisher'], date=args['date'], price=args['price'], quantity=args['quantity']
        )
        if args['genres']:
            for i in args['genres'].split(','):
                cat = session.query(Category).filter(Category.name == i).first()
                if cat is not None:
                    product.categories.append(cat)
        session.add(product)
        session.commit()
        return jsonify({'success': 'OK'})
