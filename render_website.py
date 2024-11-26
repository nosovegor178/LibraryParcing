import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
import os
import more_itertools


def get_books():
    with open("./result/books.json", "r", encoding="utf-8") as my_file:
        file_content_json = my_file.read()
        books = json.loads(file_content_json)
        return books


def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    downloaded_books = get_books()
    downloaded_books = list(more_itertools.chunked(downloaded_books, 20))
    print(downloaded_books)
    for page_number, page_json in enumerate(downloaded_books):
        rendered_page = template.render(
            books=page_json
        )

        os.makedirs('pages', exist_ok=True)

        with open('pages/index{}.html'.format(page_number+1), 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print('Server rebuilt')

rebuild()

server = Server()
server.watch('pages/*.html', rebuild)
server.serve(root='pages/index1.html')