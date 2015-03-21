from os import path, mkdir
from helper import test_app_path, clean_pages
from forgery_py import lorem_ipsum as lorem, date
import random

_title = lambda: 'title: "%s"' % lorem.words(random.randint(2, 5))
_file_name = lambda: '%s_%s' % (lorem.word(), lorem.word())
_summary = lambda: 'summary: "%s"' % lorem.sentence()
_body = lambda: lorem.paragraphs(random.randint(5, 20))
_tags = lambda: 'tags: "%s"' % ','.join(lorem.words(random.randint(2, 5), as_list=True))
_pub = lambda: 'date: %s 00:00:00' % date.date(past=True)


class DataMocks(object):
    def page(self, file_name):
        return self.write_page(file_name, [_title(), _summary(), '', _body()])

    def post(self, file_name):
        return self.write_page(file_name, [_title(), _summary(), _tags(), _pub(), '', _body()], root='pages/posts')


    def write_page(self, file_name, lines, root='pages'):
        page_folder = path.join(test_app_path, root, file_name)
        if not path.exists(page_folder):
            mkdir(page_folder)

        with open(path.join(test_app_path, root, file_name + '.md'), 'w') as file:
            file.write('\n'.join(lines))
        return self

    def index(self):
        return self.write_page('index', ['layout: recent', _title(), _summary(), '', _body()])

    def prepare(self):
        clean_pages()
        self.index()
        return self

    def posts(self):
        _posts_path = path.join(test_app_path, 'pages', 'posts')
        if not path.exists(_posts_path):
            mkdir(_posts_path)

        [self.post(_file_name()) for i in [0, random.randint(1, 20)]]
        return self

    def pages(self):
        [self.page(_file_name()) for i in [0, random.randint(1, 5)]]
        return self


m = DataMocks()
