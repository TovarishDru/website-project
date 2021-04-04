from requests import get, post, delete


"""
print(get('http://127.0.0.1:8080/api/user/1').json())
# корректно

print(get('http://127.0.0.1:8080/api/user/100').json())
# ошибка - такого id не существуетт

print(post('http://127.0.0.1:8080/api/user',
           json={'name': 'user8', 'email': 'user8@yandex.ru', 'role': 'user', 'password': '1234'
                 }).json())
# корректно

print(get('http://127.0.0.1:8080/api/user').json())
# корректно

print(delete('http://127.0.0.1:8080/api/user/8').json())
# корректно

print(delete('http://127.0.0.1:8080/api/user/100').json())
# ошибка - такого id не существует

print(post('http://127.0.0.1:8080/api/user',
           json={'name': 'user', 'email': 'user1@yandex.ru', 'role': 'user', 'password': '1234'
                 }).json())
# ошибка - пользователь с такой почтой уже существует
                 
"""
