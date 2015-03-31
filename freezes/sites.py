# -*- coding: utf-8 -*-
# !/usr/bin/python

from flask import current_app, request
from datetime import datetime
from os import walk
from werkzeug.utils import cached_property
import csv
import re


truly = lambda expr: expr is True
falsely = lambda expr: expr is False
is_none = lambda expr: expr is None
is_empty = lambda expr: expr == ''
none_or_empty = lambda obj: is_empty(obj) or is_none(obj)


class Archive(object):
    title = ''
    count = 0

    def __init__(self, **kwargs):
        self.__dict__.__init__(**kwargs)

    @property
    def posts(self):
        return [p for p in current_app.site.posts if (('%s-%s' % (p.published.year, p.published.month)) == self.title)]


def _extract_local(terms):
    if terms == '' or (terms is None):
        return ''

    results = re.match('^[a-z]{2}-[a-z]{2}', terms.lower())
    if results is not None:
        return results.group(0)
    else:
        ''


def fix_name(n):
    'Fixes a string to be nicer (usable) variable names.'
    return n.replace(' ', '_').replace('.', '_')


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def read_csv(csv_file):
    from_csv_line = lambda l, h: dict(zip(h, l))
    iter = unicode_csv_reader(csv_file).__iter__()
    headers = map(fix_name, iter.next())
    return [from_csv_line(i, headers) for i in iter]


class Site(object):
    _data = None
    lang = ''

    def __init__(self, **kwargs):
        self.__dict__.__init__(**kwargs)

    def menus(self, search_path=''):
        """Get all page in the site
        """
        # patterns = search_path.split('/')
        # if len(patterns) == 1:
        _locale = _extract_local(search_path)
        if _locale is None:
            _locale = ''

        # current_app.logger.info(_locale)

        return sorted([sp for sp in [p for p in current_app.pages if p._has_title and p._top and p._locale == _locale]],
                      key=lambda sp: sp._id)
        # else:
        # return self.query('/'.join(patterns[:1]))

    def get_pages_path(self, context_path=""):
        if is_empty(context_path) or is_none(context_path):
            return current_app.pages.get('index')
        else:
            segments = context_path.split('/')
            _path = ''
            results = []

            for _partial in segments:
                if _path == '':
                    _path = _partial
                else:
                    _path = _path + '/' + _partial
                if _path != context_path:
                    results.append(current_app.pages.get(_path))
            return results

    def locale_posts(self, locale=''):
        return (p for p in self.posts if p._locale == locale)

    def query(self, search_path, all=False, sort='id'):
        """Get post in specified collation path
        """
        posts = (p for p in current_app.pages if p._has_title and p.path.startswith(search_path) and p._is_not_post)
        if not all:
            posts = [p for p in posts if
                     (len(p.path[len(search_path) + 1:].split('/')) == 1) and (p.path != search_path)]

        return sorted(posts, key=lambda p: p.meta.get(sort, 0))

    def tagged(self, tag, locale=''):
        return (p for p in current_app.pages if
                p._has_tags and p._has_title and (tag in p._tags) and p._locale == locale)

    @property
    def pages(self):
        """Get all page in the site
        """
        _pages = (p for p in current_app.pages if p._has_title and p._is_post == False)
        return sorted(_pages, key=lambda p: p._id)

    @property
    def posts(self):
        """ Get all posts in the site
        """
        _posts = (p for p in current_app.pages if p._has_title and p._is_post)
        return sorted(_posts, reverse=True, key=lambda p: p.published)

    @cached_property
    def data(self):
        """ Auto load the data files (`/data` folder) into dict
        :return:
        """
        from os import path
        import json
        import yaml
        import logging

        # if self._data is not None:
        # return self._data

        class FriendlyDict(dict):
            def __getattr__(self, item):
                return self.get(item, None)

            def __getitem__(self, name):
                return self.get(name, None)

        self._data = FriendlyDict()
        data_path = path.join(current_app.path, 'data')

        # Define data file loaders
        _yml_loader = lambda p, n, f: p.update({n: yaml.load(f.read())})
        _csv_loader = lambda p, n, f: p.update({n: read_csv(f)})

        _loaders_ = {
            '.json': lambda p, n, f: p.update({n: json.load(f)}),
            '.yml': _yml_loader,
            '.yaml': _yml_loader,
            '.csv': _csv_loader
        }

        logging.getLogger()

        def load_data_objects(parent, dst_path):
            for root, dirs, files in walk(dst_path):

                def __load_dirs__(d):
                    parent.update({d: FriendlyDict()})
                    load_data_objects(parent.get(d), path.join(root, d))

                def __load_files__(f):
                    file_name = path.join(root, f)
                    ext = path.splitext(file_name)[1]

                    try:
                        with open(file_name) as file:
                            obj_name = path.basename(path.splitext(file_name)[0])
                            (_loaders_.get(ext, None) is not None) and _loaders_.get(ext)(parent, obj_name, file)
                    except Exception as e:
                        logging.error(e.message)
                    finally:
                        pass

                [__load_dirs__(d) for d in dirs if parent.get(d) is None and root == dst_path]
                [__load_files__(f) for f in files if root == dst_path]

        load_data_objects(self._data, data_path)
        return self._data

    @property
    def tags(self):
        tag_strings = [p.meta.get('tags', '') for p in current_app.pages if p._has_tags]
        if is_none(tag_strings) or tag_strings == []:
            return []

        tags = (','.join(tag_strings)).split(',')
        tmp = []
        [(lambda c: (not (c in tmp)) and tmp.append(c))(tag) for tag in tags]
        return tmp

    @property
    def archives(self, locale=''):
        from itertools import groupby
        from operator import itemgetter

        _posts = [('%s-%s' % (p.published.year, p.published.month), p.path) for p in self.posts if
                  (datetime.now() - p.published).days > 30 and p._locale == locale]

        _archives = []
        for key, val in groupby(sorted(_posts, reverse=True, key=itemgetter(0)), itemgetter(0)):
            archive = Archive(title=key, count=0)
            for i in val:
                archive.count += 1
            _archives.append(archive)

        return _archives