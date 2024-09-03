import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import argparse
from time import sleep


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_file(response, filename, folder='Books'):
    sanitized_filename = sanitize_filename(filename)
    path_to_file = os.path.join(folder, sanitized_filename)
    os.makedirs(folder, exist_ok=True)
    with open(path_to_file, 'wb') as file:
        file.write(response.content)


def parse_book_page(response, base_url):
    soup = BeautifulSoup(response.text, 'lxml')
    book_name, book_author = soup.find('h1').text.split(' :: ')
    book_image_url = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin(base_url, book_image_url)
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


def download_book_and_its_image(book_url, text_url):
    text_page_response = requests.get(text_url, params=params)
    text_page_response.raise_for_status()
    check_for_redirect(text_page_response)
    response = requests.get(book_url)
    check_for_redirect(response)
    response.raise_for_status()
    parsed_page = parse_book_page(response, book_url)
    book_name = '{}. {}.txt'.format(book_number,
                                    parsed_page['book_name']) 
    download_file(text_page_response, book_name, 'Books')
    response = requests.get(parsed_page['image_url'])
    response.raise_for_status()
    download_file(response,
                parsed_page['image_name'],
                'images')


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
        try:
            book_url = 'https://tululu.org/b{}/'.format(book_number)
            text_url = 'https://tululu.org/txt.php'
            params = {
                'id': '{}'.format(book_number)
            }
            download_book_and_its_image(book_url, text_url)
        except requests.exceptions.HTTPError:
            print('Книга отсутствует')
        except requests.exceptions.ConnectionError:
            print('Повторное подключение...')
            sleep(20)
