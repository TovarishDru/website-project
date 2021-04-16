import re

from requests import get


def get_substrings(string):
    """Функция разбивки на слова"""
    return re.split('\W+', string)


def get_distance(s1, s2):
    """Расстояние Дамерау-Левенштейна"""
    d, len_s1, len_s2 = {}, len(s1), len(s2)
    for i in range(-1, len_s1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len_s2 + 1):
        d[(-1, j)] = j + 1
    for i in range(len_s1):
        for j in range(len_s2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,
                d[(i, j - 1)] + 1,
                d[(i - 1, j - 1)] + cost)
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)
    return(d[len_s1 - 1, len_s2 - 1])


def check_substring(search_request, original_text, max_distance):
    """Проверка нечёткого вхождения одного набора слов в другой"""
    substring_list_1 = get_substrings(search_request)
    substring_list_2 = get_substrings(original_text)

    not_found_count = len(substring_list_1)

    for substring_1 in substring_list_1:
        for substring_2 in substring_list_2:
            if get_distance(substring_1, substring_2) <= max_distance:
                not_found_count -= 1

    if not not_found_count:
        return True


def product_search(search_request):
    ans = []
    res = get('http://127.0.0.1:8080/api/product').json()['product']
    for product in res:
        if check_substring(search_request.lower(), product['title'].lower(), max_distance=2):
            ans.append(product['id'])
        elif product['title'].lower().startswith(search_request.lower()):
            ans.append(product['id'])

    return ans

# result = check_substring(search_request, original_text, max_distance=2)

#print(result)  # True если найдено, иначе None