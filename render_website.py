import json
import os
import argparse

import more_itertools
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def get_books(user_path):
    with open(user_path, 'r', encoding='utf-8') as my_file:
        books = json.load(my_file)
        return books


def render_page(page_json, page_number, downloaded_books):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    
    rendered_page = template.render(
            books=page_json,
            pages_number=len(downloaded_books),
            current_page=page_number+1
        )
    
    os.makedirs('./pages', exist_ok=True)

    with open('./pages/index{}.html'.format(page_number+1), 'w', encoding="utf8") as file:
        file.write(rendered_page)


def rebuild():
    downloaded_books = get_books(args.user_folder)
    number_of_books_on_page = 20
    downloaded_books = list(more_itertools.chunked(downloaded_books,
                                                   number_of_books_on_page))
    for page_number, page_json in enumerate(downloaded_books):
        render_page(page_json, page_number, downloaded_books)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Downloading books and all info
        about them in the certainly range'''
    )
    parser.add_argument('--user_folder',
                        help='''The path to the results
                         of parsing. You shoud notice the file name, too''',
                        type=str,
                        default='books.json')
    args = parser.parse_args()
    
    

    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.', default_filename='./pages/index1.html')
