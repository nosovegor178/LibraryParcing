import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


directory = 'Books'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError
    

def download_file(response, filename, folder='Books'):
    sanitized_filename = sanitize_filename(filename)
    path_to_file = os.path.join(folder, sanitized_filename) 
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open((path_to_file), 'wb') as file:
        file.write(response.content)
    return path_to_file



def find_author_and_book_name_by_number(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    filename = soup.find('h1').text.split('::')
    book_name = filename[0].strip()
    author_name = filename[1].strip()
    return book_name, author_name


def get_book_image_url(book_url):
    response = requests.get(book_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_image_url = soup.find('div', class_='bookimage').find('img')['src']
    parsed_url = urljoin('https://tululu.org', book_image_url)
    return parsed_url


def get_book_comments(book_url):
    try:
        response = requests.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book_comments = soup.find_all('div', class_='texts')
        founded_book_comments = []
        for one_comment in book_comments:
            founded_book_comments.append(one_comment.find('span').text)
        return founded_book_comments
    except AttributeError:
        return []


def get_N_number_of_books(N):
    for book_number in range(1, N+1):
        try:
            book_url = 'https://tululu.org/b{}'.format(book_number)
            # url_for_downloading = 'https://tululu.org/txt.php?id={}'.format(book_number)
            # response = requests.get(url_for_downloading)
            # response.raise_for_status() 
            # check_for_redirect(response)
            # book_name = '{}. {}.txt'.format(book_number, find_author_and_book_name_by_number(book_url)[0])
            # image_url = get_book_image_url(book_url)
            # image_name = urlparse(image_url).path.split('/')[-1]
            # response = requests.get(image_url)
            # response.raise_for_status()
            # check_for_redirect(response)
            # download_file(response, image_name, 'images')
            # download_file(response, book_name)
            # comments = get_book_comments(book_url)
        except requests.exceptions.HTTPError:
            print('Книга отсутствует')

