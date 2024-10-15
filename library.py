import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import argparse
from time import sleep
import json


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_file(response, filename, folder):
    sanitized_filename = sanitize_filename(filename)
    path_to_file = os.path.join(folder, sanitized_filename)
    os.makedirs(folder, exist_ok=True)
    with open(path_to_file, 'wb') as file:
        file.write(response.content)


def parse_book(path_to_result, book_id, book_url, book_page):
    soup = BeautifulSoup(book_page.text, 'lxml')
    book_name, book_author = soup.select_one('h1').text.split(' :: ')
    book_image_url = soup.select_one('.bookimage img')['src']
    image_url = urljoin(book_url, book_image_url)
    book_comments = soup.select('.texts')
    comments = [comment.select_one('span').text for comment in book_comments]
    genres = soup.select('span.d_book a')
    genres = [genre.text for genre in genres]
    parsed_book = {
        'author': book_author.strip(),
        'book_name': book_name.strip(),
        'book_genres': genres,
        'comments': comments,
        'book_id': book_id.strip('/')[1:],
        'image_url': image_url,
        'image_name': urlparse(image_url).path.split('/')[-1],
        'dest_img_url': f'{path_to_result}/images',
        'dest_books_url': f'{path_to_result}/books'
    }
    return parsed_book


def parse_books_page(path_to_result, page):
    parsed_page = []
    for book in page:
        book_url_template = 'https://tululu.org/'
        book_id = book.select_one('a')['href']
        book_url = urljoin(book_url_template, book_id)
        book_page = requests.get(book_url)
        parsed_page.append(parse_book(path_to_result, book_id, book_url, book_page))
    return parsed_page


def download_image(path_to_dir, image_name, image_url):
    response = requests.get(image_url)
    response.raise_for_status()
    download_file(response, image_name, path_to_dir)


def download_book(path_to_dir, text_url, filename, params):
    text_page_response = requests.get(text_url, params=params)
    text_page_response.raise_for_status()
    check_for_redirect(text_page_response)
    download_file(text_page_response, filename, path_to_dir)


def parse_category(path_to_result, start_page, end_page):
    parsed_pages = []
    for page in range(start_page, end_page):
        try:
            url = f'https://tululu.org/l55/{page}/'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            books = soup.select('table.d_book')
            parsed_page = parse_books_page(path_to_result, books)
            parsed_pages.append(parsed_page)
        except requests.exceptions.ConnectionError:
                print('Повторное подключение...')
                sleep(20)
        except requests.exceptions.HTTPError:
                print('Ошибка запроса')
    return parsed_pages


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Downloading books and all info
        about them in the certainly range'''
    )
    parser.add_argument('--dest_folder',
                        help='''The path to the results
                         of parsing''',
                        type=str,
                        default='result')
    parser.add_argument('--skip_imgs',
                        help='''Skip downloading images or not''',
                        action='store_true')
    parser.add_argument('--skip_txt',
                        help='''Skip downloading books or not''',
                        action='store_true')
    parser.add_argument('--start_page',
                        help='''The number of page from which
                        you are going to download''',
                        type=int,
                        default=1)
    parser.add_argument('--final_page',
                        help='''The number of page which
                        will stop your downloading (without including)''',
                        type=int,
                        default=702)
    args = parser.parse_args()


    parsed_pages = parse_category(args.dest_folder, args.start_page, args.final_page)
    for parsed_page in parsed_pages:
        for book in parsed_page:
            try:
                if not args.skip_imgs:
                    download_image(book['dest_img_url'], book['image_name'], book['image_url'])
                if not args.skip_txt:
                    params = {
                        'id': book['book_id']
                    }
                    book_name = book['book_name']
                    download_book(book['dest_books_url'], 'https://tululu.org/txt.php', f'{book_name}.txt', params)
            except requests.exceptions.HTTPError:
                print('Книга отсутствует')
            except requests.exceptions.ConnectionError:
                print('Повторное подключение...')
                sleep(20)
    os.makedirs(args.dest_folder, exist_ok=True)
    with open(f'{args.dest_folder}/books.json', 'w', encoding='utf-8') as file:
        json.dump(parsed_pages, file, ensure_ascii=False)