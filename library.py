import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse



def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError
    

def download_file(url, filename, folder='Books'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    sanitized_filename = sanitize_filename(filename)
    path_to_file = os.path.join(folder, sanitized_filename) 
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open((path_to_file), 'wb') as file:
        file.write(response.content)
    return path_to_file


def find_author_and_book_name(response):
    soup = BeautifulSoup(response.text, 'lxml')
    filename = soup.find('h1').text.split('::')
    book_name = filename[0].strip()
    author_name = filename[1].strip()
    return book_name, author_name


def get_book_image_url(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_image_url = soup.find('div', class_='bookimage').find('img')['src']
    parsed_url = urljoin('https://tululu.org', book_image_url)
    return parsed_url


def get_book_comments(response):
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        book_comments = soup.find_all('div', class_='texts')
        founded_book_comments = []
        for one_comment in book_comments:
            founded_book_comments.append(one_comment.find('span').text)
        return founded_book_comments
    except AttributeError:
        return []
    

def get_book_genres(response):
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        genres = soup.find('span', class_='d_book').find_all('a')
        founded_genres = []
        for one_genre in genres:
            founded_genres.append(one_genre.text)
        return founded_genres
    except AttributeError:
        return []


def parse_book_page(content, book_number):
    parsed_data = []
    try:
        url_for_checking = 'https://tululu.org/txt.php?id={}'.format(book_number)
        response = requests.get(url_for_checking)
        response.raise_for_status()
        check_for_redirect(response)
        
        book_name = '{}. {}.txt'.format(book_number, find_author_and_book_name(content)[0])
        comments = get_book_comments(content)
        image_url = get_book_image_url(content)
        image_name = urlparse(image_url).path.split('/')[-1]
        genres = get_book_genres(content)
        parsed_data.append({
            'book_name': book_name,
            'book_genres': genres,
            'comments': comments,
            'image_url': image_url,
            'image_name': image_name
        })
    except requests.exceptions.HTTPError:
        print('Книга отсутствует')
    return parsed_data


def parse_all_books(books_number):
    parsing_results = []
    for book_number in range(1, books_number+1):
        book_url = 'https://tululu.org/b{}'.format(book_number)
        response = requests.get(book_url)
        response.raise_for_status()
        parsing_results.append(parse_book_page(response, book_number))
    return parsing_results

books_number = int(input('Введите желаемое количество книг: '))
print(parse_all_books(books_number))