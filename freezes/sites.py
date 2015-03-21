from flask import current_app
from datetime import datetime
import re
from os import walk

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


class Site(object):
    _data = None

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

        #current_app.logger.info(_locale)

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

    @property
    def data(self):
        """ Auto load the data files (`/data` folder) into dict
        :return:
        """
        from os import path
        import json
        import yaml
        import logging

        if self._data is not None:
            return self._data

        self._data = dict()

        for root, dirs, files in walk(path.join(current_app.path, 'data')):
            for f in files:
                file_name = path.join(root, f)
                ext = path.splitext(file_name)[1]

                try:
                    with open(file_name) as file:
                        obj_name = path.basename(path.splitext(file_name)[0])
                        if ext == '.json':
                            self._data.update({obj_name: json.load(file)})
                        if ext == '.yml':
                            self._data.update({obj_name: yaml.load(file.read())})
                except Exception as e:
                    logging.getLogger()
                    logging.error(e.message)
                    continue

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