# coding=utf-8
# !/usr/bin/python

__author__ = 'Ray'

import sys
import yaml
import logging

from os import path, getcwd

from flask import Flask
from flask_flatpages import FlatPages
from flask_bootstrap import Bootstrap
from flask_assets import Environment, YAMLLoader

from livereload import Server
from werkzeug.routing import BaseConverter
from sites import Site

from config import Config
from views import create_views
from scripts import create_scripts, SiteGenerator
from pagext import extend_pages

logging.getLogger().setLevel(logging.INFO)
basedir = path.abspath(path.dirname(__file__))


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def create_app(config):
    def _initialize(app):
        """Load the external website settings and assets configurations into current application
        :param app:
        :return:
        """
        if app.initialized:
            return app

        cwd = app.path
        # getcwd()
        config_file = path.join(cwd, '_config.yml')
        asset_file = path.join(cwd, "_assets.yml")

        if path.exists(config_file):
            settings = yaml.load(open(config_file).read())
            app.site = Site(**settings)
        else:
            raise IOError('System initialize fail: the `_config.yml` can not be found in the root of current website.')

        path.exists(asset_file) and app.assets_env.register(YAMLLoader(asset_file).load_bundles())

        app.url_map.converters['regex'] = RegexConverter
        app.initialized = True

        return app

    app = Flask(__name__, static_url_path='/static/vendors')
    app.config.from_object(config)

    Bootstrap(app)
    app.pages = FlatPages(app)
    app.assets_env = Environment(app)
    app.path = config.APP_PATH
    app.init = lambda: _initialize(app)
    app.initialized = False
    app.url_map.converters['regex'] = RegexConverter

    return app


def keep_alive(app, build_func):
    """Run the server and keep it reload and rebuild when contents changed
    :return:
    """
    live_server = Server(app.wsgi_app)

    #[live_server.watch(path.join(app.path, p), build_func) for p in
    # ['pages', 'static', 'templates', '_assets.yml', '_config.yml']]

    live_server.watch(app.path)
    live_server.serve()


def main():
    app_name = path.basename(getcwd())
    app = create_app(Config())

    create_views(app_name, app)
    extend_pages(app_name)

    if len(sys.argv[1:]) > 0:
        create_scripts(app).run()
    else:
        import webbrowser
        # from subprocess import Popen

        app.init()

        def live_rebuild():
            """
            Call the build script to generate the static website content
            :return:
            """
            site_generator = SiteGenerator(app)
            site_generator.run()

        webbrowser.open_new_tab('http://localhost:5500')
        keep_alive(app, live_rebuild)

    return app