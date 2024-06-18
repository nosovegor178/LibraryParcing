import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import argparse
from time import sleep


def do_request_to_site(book_number):
    url = 'https://tululu.org/txt.php'
    params = {
        'id': '{}'.format(book_number)
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response


def check_for_redirect(book_number):
    response = do_request_to_site(book_number)
    if response.history:
        raise requests.exceptions.HTTPError


def download_file(url, filename, folder='Books', params={}):
    response = requests.get(url, params=params)
    response.raise_for_status()
    sanitized_filename = sanitize_filename(filename)
    path_to_file = os.path.join(folder, sanitized_filename)
    os.makedirs(folder, exist_ok=True)
    with open((path_to_file), 'wb') as file:
        file.write(response.content)
    return path_to_file


def parse_book_page(response, template_url='https://tululu.org'):
    soup = BeautifulSoup(response.text, 'lxml')
    book_name, book_author = soup.find('h1').text.split(' :: ')
    book_image_url = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin(template_url, book_image_url)
    image_name = urlparse(image_url).path.split('/')[-1]
    book_comments = soup.find_all('div', class_='texts')
    comments = [comment.find('span').text for comment in book_comments]
    genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres]
    parsed_parametrs = {
        'author': book_author.strip(),
        'book_name': book_name.strip(),
        'book_genres': genres,
        'comments': comments,
        'image_url': image_url,
        'image_name': image_name
    }
    return parsed_parametrs


def download_all_books_and_their_images(book_number):
    parsing_results = []
    try:
        check_for_redirect(book_number)
        book_url = 'https://tululu.org/b{}'.format(book_number)
        response = requests.get(book_url)
        response.raise_for_status()
        parsed_page = parse_book_page(response)
        parsing_results.append(parsed_page)
        url = 'https://tululu.org/txt.php'
        params = {
            'id': '{}'.format(book_number)
        }
        book_name = '{}. {}.txt'.format(book_number,
                                        parsed_page['book_name'])
        download_file(url, book_name, 'Books', params)
        download_file(parsed_page['image_url'],
                    parsed_page['image_name'],
                    'images')
    except requests.exceptions.HTTPError:
        print('Книга отсутствует')
    except requests.exceptions.ConnectionError:
        print('Повторное подключение...')
        sleep(20)
    return parsing_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Downloading books and all info
        about them in the certainly range'''
    )
    parser.add_argument('start_id',
                        help='''The number of book from which
                        you are going to download''',
                        type=int)
    parser.add_argument('end_id',
                        help='''The number of book which
                        will stop your downloading''',
                        type=int)
    args = parser.parse_args()
    for book_number in range(args.start_id, args.end_id+1):
        download_all_books_and_their_images(book_number)
