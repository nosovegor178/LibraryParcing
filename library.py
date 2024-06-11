import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import argparse


def check_for_redirect(book_number):
    url = 'https://tululu.org/txt.php?id={}'.format(book_number)
    response = requests.get(url)
    response.raise_for_status()
    if response.history:
        raise requests.exceptions.HTTPError
    

def download_file(url, filename, folder='Books'):
    response = requests.get(url)
    response.raise_for_status()
    sanitized_filename = sanitize_filename(filename)
    path_to_file = os.path.join(folder, sanitized_filename) 
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open((path_to_file), 'wb') as file:
        file.write(response.content)
    return path_to_file


def parse_book_page(book_url, template_url = 'https://tululu.org'):
    response = requests.get(book_url)
    response.raise_for_status()
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


def parse_all_books(start_id, end_id):
    parsing_results = []
    for book_number in range(start_id, end_id+1):
        try:
            check_for_redirect(book_number)
            book_url = 'https://tululu.org/b{}'.format(book_number)
            parsing_results.append(parse_book_page(book_url))
        except requests.exceptions.HTTPError:
            print('Книга отсутствует')
    return parsing_results


def download_all_books_and_their_images(start_id, end_id):
    for book_number in range(start_id, end_id+1):
        try:
            check_for_redirect(book_number)
            url = 'https://tululu.org/txt.php?id={}'.format(book_number)
            book_url = 'https://tululu.org/b{}'.format(book_number)
            book_name = '{}. {}.txt'.format(book_number,
                                        parse_book_page(book_url)['book_name'])
            download_file(url, book_name)
            download_file(parse_book_page(book_url)['image_url'],
                            parse_book_page(book_url)['image_name'],
                            'images')
        except requests.exceptions.HTTPError:
            print('Книга отсутствует')


parser = argparse.ArgumentParser()
parser.add_argument('start_id',
                    help='The number of book from which you are going to download',
                    type=int)
parser.add_argument('end_id', 
                    help='The number of book which will stop your downloading',
                    type=int)
args = parser.parse_args()


if __name__ == '__main__':
    download_all_books_and_their_images(args.start_id, args.end_id)
    print(parse_all_books(args.start_id, args.end_id))