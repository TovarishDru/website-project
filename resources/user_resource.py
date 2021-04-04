from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.__all_models import User
from resources.user_parser import parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def abort_if_user_exists(email):
    session = db_session.create_session()
    if session.query(User).filter(User.email == email).first():
        abort(409, message=f'User with email {email} already exists')


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'name', 'email', 'role', 'hashed_password'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'name', 'email', 'role', 'hashed_password')) for item in news]})

    def post(self):
        args = parser.parse_args()
        abort_if_user_exists(args['email'])
        session = db_session.create_session()
        user = User(
            name=args['name'], role=args['role'], email=args['email']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
