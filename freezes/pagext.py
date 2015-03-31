#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import current_app, url_for
from markdown import markdown
from flask_flatpages import Page
from os import path
import re
from datetime import datetime


def get_excerpt(self):
    """Get the post excerpt from post body
    :return:
    """
    if self.body == '':
        return ''

    lines = self.body.split('\n')
    excerpt_lines = []

    for line in lines:
        if line.startswith('#') or line.startswith('!') or line.startswith('[TOC]'):
            continue
        excerpt_lines.append(line)

        if len(excerpt_lines) >= 3:
            break

    if len(excerpt_lines) > 0:
        return markdown("\n".join(excerpt_lines))

    return ''


def get_relative_posts(self):
    if self.path.startswith('posts'):
        if self._has_tags:
            primary_tag = self._tags[0]
            return [p for p in current_app.site.posts if
                    p._has_tags and (p.path != self.path) and (primary_tag in p._tags)]
        else:
            return []
    else:
        return [p for p in current_app.site.query(self.path) if p.path != self.path]


def get_next_post(self):
    try:
        if self._is_post:
            _posts = current_app.site.posts
        else:
            _posts = current_app.site.query(self._parent_path)

        return _posts[_posts.index(self):][1]
    except:
        return None


def get_prev_post(self):
    try:
        if self._is_post:
            _posts = current_app.site.posts
        else:
            _posts = current_app.site.query(self._parent_path)

        return _posts[:_posts.index(self)][-1]
    except:
        return None


def get_wordcount(self):
    import re

    if self.html != '':
        regex = re.compile(r'(<([^>]+)>)', re.I)
        clean_text = re.sub(regex, '', self.html).strip('\n')
        return len(clean_text)
    return 0


def get_published(self):
    user_defined = self.meta.get('date', '')
    if user_defined == '':
        return self.last_updated
    else:
        return user_defined


def get_tags(self):
    tags_str = self.meta.get('tags', '')
    if tags_str == '':
        return []
    return tags_str.split(',')


def get_local_name(self):
    pattern = '^[a-z]{2}-[a-z]{2}'
    results = re.match(pattern, self.path.lower())
    if results is not None:
        return results.group(0)
    else:
        return ''


def to_json(self):
    return {
        'id': self._id,
        'name': self.name,
        'path': self.path,
        'url': self.url,
        'excerpt': self.excerpt,
        'body': self.body,
        'tags': self._tags,
        'created': self.created,
        'last_updated': self.last_updated,
        'published': self.published,
        'meta': self.meta
    }


def extend_pages(app_name):
    Page.excerpt = property(get_excerpt)
    Page.relatives = property(get_relative_posts)
    Page.next = property(get_next_post)
    Page.prev = property(get_prev_post)
    Page.url = property(lambda self: url_for('%s.index' % app_name, page_path=self.path))
    Page.name = property(lambda self: self.path.split('/')[-1])
    Page.wordcount = property(get_wordcount)

    Page._filename = property(lambda self: path.join(current_app.path, 'pages', self.path + '.md'))

    Page.created = property(lambda self: datetime.fromtimestamp(path.getctime(self._filename)))
    Page.last_updated = property(lambda self: datetime.fromtimestamp(path.getmtime(self._filename)))
    Page.published = property(get_published)

    Page._locale = property(get_local_name)
    Page._is_default = property(lambda self: self.name == 'index' or self.name == self._locale)
    Page._is_post = property(
        lambda self: self.path.startswith('posts') or (
            self._locale != '' and (len(self.path.split('/')) > 1 and self.path.split('/')[1] == 'posts')))
    Page._is_not_post = property(lambda self: not self._is_post)
    Page._top = property(lambda self: '/' not in self.path or ((self._locale + '/' + self.name) == self.path ))
    Page._parent_path = property(lambda self: '/'.join(self.path.split('/')[:-1]))
    Page._has_title = property(lambda self: 'title' in self.meta)
    Page._has_tags = property(lambda self: 'tags' in self.meta)
    Page._tags = property(get_tags)
    Page._id = property(lambda self: self.meta.get('id', 0))
    Page.to_json = property(to_json)
