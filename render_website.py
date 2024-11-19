from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def get_books():
    with open("./result/books.json", "r", encoding="utf-8") as my_file:
        file_content_json = my_file.read()
        books = json.loads(file_content_json)
        my_file.close()
        return books


def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('templates/template.html')
    downloaded_books = get_books()
    rendered_page = template.render(
        books=downloaded_books
    )

    with open('templates/index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print('Server rebuilt')

rebuild()

server = Server()
server.watch('templates/*.html', rebuild)
server.serve(root='templates/index.html')