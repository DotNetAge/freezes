__author__ = 'Ray'

from flask import g, render_template, send_from_directory, Blueprint, current_app, url_for, jsonify
from os import path
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
from fnmatch import fnmatch
from datetime import datetime
from werkzeug.exceptions import abort
from flask_babel import gettext, refresh


class SimplePage(object):
    title = ''
    path = ''
    _locale = ''
    _is_default = False

    def __init__(self, title=''):
        self.title = title


def set_lang(locale_name):
    if locale_name != '':
        g.lang = locale_name.split('-')[0]
        refresh()


def create_views(name, app):
    main = Blueprint(name, name,
                     template_folder='templates',
                     static_url_path='/static',
                     static_folder='static')

    try:
        if app.config['TESTING'] is False:
            pkg_file = path.join(app.path, '__init__.py')
            if path.exists(pkg_file):
                import imp

                ext_module = imp.load_source(name, pkg_file)
                routes_func_name = 'register'
                if hasattr(ext_module, routes_func_name) and callable(getattr(ext_module, routes_func_name)):
                    ext_module.register(main)
    finally:
        __init_views(main, app)
        app.register_blueprint(main)
        return main


def __init_views(main, app):
    @main.route('/')
    @main.route('/<path:page_path>/')
    def index(page_path='index'):

        if fnmatch(page_path, '*.*'):
            _abs_path = path.abspath(path.join('pages', path.dirname(page_path)))
            return send_from_directory(_abs_path,
                                       path.basename(page_path))

        page = current_app.pages.get_or_404(page_path)
        default_layout = 'page'
        if page._is_post:
            default_layout = 'post'

        set_lang(page._locale)

        template = 'layouts/%s.html' % page.meta.get('layout', default_layout)
        return render_template(template, page=page, locale=page._locale, site=current_app.site)

    @main.route('/api/pages/<path:search_path>.json')
    def data_pages(search_path):
        if search_path == 'all':
            return jsonify(pages=[p.to_json for p in current_app.site.pages])
        else:
            _page = current_app.pages.get_or_404(search_path)
            json_page = _page.to_json
            json_page.update(pages=[p.to_json for p in current_app.site.query(search_path)])
            return jsonify(json_page)

    @main.route('/api/posts.json')
    def data_posts():
        return jsonify(posts=[p.to_json for p in current_app.site.posts])

    @main.route('/<regex("[a-z]{2}-[A-Z]{2}"):locale_name>/tags/')
    @main.route('/tags/')
    def tags(locale_name=''):
        set_lang(locale_name)

        return render_template('layouts/tags.html',
                               page=SimplePage('All tags'),
                               site=current_app.site,
                               locale=locale_name)

    @main.route('/<regex("[a-z]{2}-[A-Z]{2}"):locale_name>/tags/<name>/')
    @main.route('/tags/<name>/')
    def tag(name, locale_name=''):
        set_lang(locale_name)
        if (name is None) or name == '':
            abort(404)

        return render_template('layouts/tagged.html',
                               page=SimplePage(gettext(u'Articles tagged with:%(value)s', value=name)),
                               tag=name,
                               locale=locale_name,
                               site=current_app.site)

    @main.route('/<regex("[a-z]{2}-[A-Z]{2}"):locale_name>/archives/')
    @main.route('/archives/')
    def archives(locale_name=''):
        set_lang(locale_name)
        return render_template('layouts/archives.html',
                               page=SimplePage(gettext(u'All archives')),
                               locale=locale_name,
                               site=current_app.site)

    @main.route('/<regex("[a-z]{2}-[A-Z]{2}"):locale_name>/archives/<name>')
    @main.route('/archives/<name>')
    def archive(name, locale_name=''):

        set_lang(locale_name)
        results = [a for a in current_app.site.archives if a.title == name]

        if len(results) == 0:
            abort(404)

        return render_template('layouts/archived.html',
                               page=SimplePage(gettext(u'Archive:%(value)s', value=name)),
                               locale=locale_name,
                               archive=results[0],
                               site=current_app.site)

    def render_404():
        """Render the not found page
        """
        return render_template('404.html', page={'title': gettext(u'Page not found'), 'path': '404'},
                               locale='',
                               site=current_app.site)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_404(), 404


    @main.route('/404.html')
    def static_404():
        return render_404()


    @app.route('/sitemap.xml')
    def sitemap():
        locations = [(lambda p: (post.url, post.last_updated))(post) for post in current_app.pages]
        sites = [(current_app.site.url + l[0], l[1]) for l in locations]
        return render_template('sitemap.xml', sites=sites), 200, {'Content-Type': 'application/xml; charset=utf-8'}


    @app.route('/feeds/<path:name>.xml')
    def feed(name='recent'):
        _feed_url = url_for('.feed', name=name, _external=True)

        _posts = current_app.site.posts

        if name != 'recent':
            _posts = current_app.site.query(name, all=True)

        feed = AtomFeed(gettext('Recent posts'),
                        feed_url=_feed_url,
                        url=current_app.site.url)

        # if len(_posts) > 20:
        # _posts = _posts[20]

        for post in _posts:
            feed.add(post.meta.get('title', ''),
                     unicode(post.html),
                     content_type='html',
                     subtitle=post.meta.get('summary', ''),
                     author=post.meta.get('author'),
                     url=urljoin(current_app.site.url, post.url),
                     updated=post.last_updated,
                     published=post.published)

        return feed.get_response()


