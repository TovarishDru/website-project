from flask_restful import reqparse

parser = reqparse.RequestParser()

parser.add_argument('title', required=True)
parser.add_argument('description', required=True)
parser.add_argument('picture', required=True)
parser.add_argument('developer', required=True)
parser.add_argument('publisher', required=True)
parser.add_argument('date', required=True)
parser.add_argument('price', required=True, type=int)
parser.add_argument('quantity', required=True, type=int)
parser.add_argument('genres', required=False)
