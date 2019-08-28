"""
python 3.7.4
Поиск вакансий по ключевым словам.
Полное описание API: https://github.com/hhru/api
Autor: uncleJasper
"""

import os
import csv
import requests

import time
from datetime import  timedelta

"""
area:
    113 - Россия
    1146 - Красноярский край
        54 - Красноярск
    1202 - Новосибирская область
        4 - Новосибирск
    справочник: https://api.hh.ru/areas
    Можно передать несколько значений в виде множества.
"""
AREA = ('54', '4')
KEYWORDS = [
    'sap',
    'abap',
    'python',
    'django',
    'flask',
    'data scientist'
]


def run():
    """
    Главная функция
    :return:
    """
    start = time.time()
    for keyword in KEYWORDS:
        pars_vacancy(keyword)
    end = time.time()
    print(f'Done!\nЗатрачено времени: {timedelta(seconds=(end - start))}')


def pars_vacancy(search_word):
    """
    Поиск вакансий по ключевому слову и сохранение результатов.
    :param search_word: слово для поиска
    :return:
    """
    list_vacancy = []

    result = get_response(search_word)
    if result['found'] > 0:
        list_vacancy.extend(result['items'])
        all_pages = int(result['pages'])
        if all_pages > 1:
            for page in range(1, all_pages):
                result = get_response(search_word, page)
                list_vacancy.extend(result['items'])
        save_result_to_csv(search_word, list_vacancy)
    else:
        print(f'По ключевому слову "{search_word}" ничего не найдено')


def get_response(search_word, page=0):
    """
    Получим данные
    :param search_word: слово для поиска
    :param page: номер страницы. По умолчанию page = 0
    :return:
    """
    api_url = 'https://api.hh.ru/vacancies'

    par = {
        'text': search_word,
        'area': AREA,
        'per_page': 100,
        'page': page
    }

    response = requests.get(api_url, params=par)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Ошибка при поиске по слову: {search_word}')


def save_result_to_csv(search_word, list_items):
    """
    Сохранение найденых вакансий в файл *.csv
    :param search_word: слово для поиска
    :param list_items: список найденых результатов
    :return:
    """
    if os.path.exists('results') is False:
        os.makedirs('results')
    file_name = 'results\\' + search_word + '.csv'
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([
            'Город',
            'Наименование',
            'з/п',
            'Ссылка на текущую вакансию',
            'Архивная',
            'Опубликована',
            'Работодатель'
        ])
        for item in list_items:
            salary = ""
            if item['salary'] is not None:
                salary_fr = item['salary']['from']
                salary_to = item['salary']['to']
                salary_cur = item['salary']['currency']
                if salary_fr:
                    salary = f'от {salary_fr}'
                if salary_to:
                    salary = f'{salary} до {salary_to}'
                salary = f'{salary} {salary_cur}'
            else:
                salary = "не указана"

            try:
                writer.writerow([
                    item['area']['name'],
                    item['name'],
                    salary,
                    item['alternate_url'],
                    item['archived'],
                    item['published_at'][:10],
                    item['employer']['name']
                ])
            except UnicodeEncodeError:
                writer.writerow([
                    item['area']['name'],
                    '',
                    salary,
                    item['alternate_url'],
                    item['archived'],
                    item['published_at'][:10],
                    '',
                ])


if __name__ == '__main__':
    run()
