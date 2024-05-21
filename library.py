import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


directory = 'Books'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError
    

def download_txt(url, filename, folder='Books'):
    sanitized_filename = sanitize_filename(filename)
    path_to_file = os.path.join(folder, sanitized_filename) 
    response = requests.get(url)
    response.raise_for_status() 
    check_for_redirect(response)
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open((path_to_file), 'wb') as file:
        file.write(response.content)
    return path_to_file


def find_author_and_book_name_by_number(N):
    url = "https://tululu.org/b{}".format(N)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    filename = soup.find('h1').text.split('::')
    try:
        book_name = filename[0].strip()
        author_name = filename[1].strip()
        return book_name, author_name
    except IndexError:
        return('Нет такой книги')


def get_N_number_of_books(N):
    for book_number in range(1, N+1):
        try:
            book_name = '{}. {}.txt'.format(book_number, find_author_and_book_name_by_number(book_number)[0])
            url = "https://tululu.org/txt.php?id={}".format(book_number)
            download_txt(url, book_name)
        except requests.exceptions.HTTPError:
            print('Книга отсутствует')


get_N_number_of_books(10)