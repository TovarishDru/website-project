# website-project
https://disk.yandex.ru/d/8gdLEWeKkxf43A?w=1



<------>
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>AllGames</title>
        <link rel="stylesheet" 
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" 
                    integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" 
                    crossorigin="anonymous">
        <link rel='stylesheet' href='/static/css/style.css'>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.4.1/font/bootstrap-icons.css">
        <link rel="shortcut icon" href="/static/icons/logo.png" type="image/png">
    </head>
    <body>
        <div class='wrapper'>
            <header class='container-fluid' id='menu'>
                <div class='row'>
                <ul class='menu_list'>
                    <li class='col' id='header_col'>
                        <a href='/' class="header_icon"><img src='/static/icons/main.png'></a>
                    </li>
                    <li class='col' id='header_col'>
                        <a href='#' id='header_href'>
                            Жанры
                        </a>
                        <ul class="sub_menu_list">
                            <br>
                            <div class='sub_cont'>
                                {% for i in genres %}
                                    <li class='sub_menu_link'>
                                        <a href='/search/category={{ i.name }}'>{{i.name}}</a>
                                    </li>
                                {% endfor %}
                            </div>
                        </ul>
                    </li>
                    <li class='col col-5' id='header_col'>
                        <form action="" method="post" class='search_box'>
                            <input type='text' name='search' class='search_txt'>
                            <i class="bi bi-search"></i>
                        </form>
                        <div class="error_message">
                            {{message}}
                        </div>
                    </li>
                    <li class='col' id='header_col'>
                        {% if current_user.is_authenticated and current_user.role == 'admin' %}
                        <a href='/games'><img src="/static/icons/add.png" class='nav_ic'></a>
                        {% elif current_user.is_authenticated and current_user.role == 'user' %}
                            <a href='/cart'><img src="/static/icons/cart.png" class='nav_ic'></a>
                        {% endif %}
                    </li>
                    <li class='col' id='header_col'>
                        {% if current_user.is_authenticated and current_user.role == 'admin' %}
                            <a href='/news_list' id='header_href'>Новости</a>
                        {% elif current_user.is_authenticated and current_user.role == 'user' %}
                            <a href='/news' id='header_href'>Предложить новость</a>
                        {% endif %}
                    </li>
                    <li class='col' id='header_col'>
                        {% if current_user.is_authenticated %}
                            <a class="navbar-brand" href="/logout" id='header_href'>Выйти</a>
                        {% else %}
                            <a href='#' id='header_href'>Войти</a>
                            <ul class="sub_menu_list">
                                <br>
                                <li>
                                    <a href="/register" class='sub_menu_link'>Регистрация</a>
                                </li>
                                <li>
                                    <a href="/login" class='sub_menu_link'>Вход</a>
                                </li>
                            </ul>
                        {% endif %}
                    </li>
                </ul>
                </div>
            </header>
            <div class='cont'>
                {% block content %}{% endblock %}
            </div>
            <footer class='container' id='footer'>
            <br>
            <div class="row">
                <div class='col col-3' id='footer_div'>
                    <img src="/static/icons/main.png">
                </div>
                <div class='col col-3' id='footer_div'>
                    <a href='#'>Вакансии</a>
                </div>
                <div class='col col-3' id='footer_div'>
                    <a href='#'>Поддержка</a>
                </div>
                <div class='col col-3' id='footer_div'>
                    <a href='#'>О компании</a>
                </div>
            </div>
            <div>
                <img src='/static/icons/footericon.png' class="warranty_img">
                <div class='warranty'>
                    Все продаваемые ключи закупаются у официальных дистрибьюторов и издателей
                </div>
            </div>
            <div class='copyright'>
                © 2021-{{year}} AllGames
            </div>
        </footer>
        </div>
    </body>
</html>
<------>



<------>
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>AllGames</title>
        <link rel="stylesheet" 
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" 
                    integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" 
                    crossorigin="anonymous">
        <link rel='stylesheet' href='/static/css/style.css'>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.4.1/font/bootstrap-icons.css">
        <link rel="shortcut icon" href="/static/icons/logo.png" type="image/png">
    </head>
    <body>
        {% block content %}{% endblock %}
    </body>
</html>
<------>
