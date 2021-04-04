from requests import get, post, delete, put


"""
print(get('http://127.0.0.1:8080/api/product/1').json())
# корректно

print(get('http://127.0.0.1:8080/api/product/100').json())
# ошибка - такого id не существуетт

print(post('http://127.0.0.1:8080/api/product',
           json={'title': 'Title', 'description': 'description', 'picture': 'picture',
                 'developer': 'developer', 'publisher': 'publisher', 'date': 'date',
                 'price': 25, 'quantity': 5, 'genres': 'экшн'}).json())
# корректно

print(put('http://127.0.0.1:8080/api/product/4',
           json={'title': 'Title5', 'description': 'description', 'picture': 'picture',
                 'developer': 'developer', 'publisher': 'publisher', 'date': 'date',
                 'price': 25, 'quantity': 5, 'genres': 'экшн,гонки'}).json())
# корректно

print(get('http://127.0.0.1:8080/api/product').json())
# корректно

print(delete('http://127.0.0.1:8080/api/product/4').json())
# корректно

print(delete('http://127.0.0.1:8080/api/product/100').json())
# ошибка - такого id не существует
"""
