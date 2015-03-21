# coding=utf-8
# !/usr/bin/python

__author__ = 'Ray'

from flask import json
from flask_frozen import Freezer
from shutil import copy, rmtree
from os import path, mkdir, getcwd, walk, remove
from flask_assets import ManageAssets
from flask.ext.script import Manager, Command, Option
import logging


class SiteGenerator(Command):
    def __init__(self, app):
        self.app = app

    def run(self):
        app = self.app
        app.init()
        freezer = Freezer(app)

        logging.getLogger().setLevel(logging.INFO)
        logging.info('Generating static pages...')

        @freezer.register_generator
        def generate_pages():
            for p in app.pages:
                if p.path == 'index':
                    yield '/'
                #logging.info('Generating %s' % p.url)
                yield p.url

        @freezer.register_generator
        def generate_datafiles():
            yield '/api/pages/all.json'
            yield '/api/posts.json'
            for p in app.pages:
                yield '/api/pages/%s.json' % p.path

        freezer.freeze()
        logging.info('Generation completed.Doing cleanup....')

        for root, dirs, files in walk(path.join(getcwd(), 'builds')):
            for d in dirs:
                if path.basename(d) in ['.webassets-cache', '_styles', '_scripts']:
                    rmtree(path.join(root, d))

            for f in files:
                if path.splitext(f)[1] in ['.less', '.scss', '.coffee']:
                    remove(path.join(root, f))
        #logging.info('Static site generation done!')


class SkeletonGenerator(Command):
    def __init__(self, app):
        self.app = app

    def get_options(self):
        return [
            Option('-n', '--name', dest='name', default=''),
        ]

    def run(self, name=''):
        """Setup new website
        """
        logging.getLogger().setLevel(logging.INFO)

        cwd =self.app.path
        #getcwd()
        basedir = path.abspath(path.dirname(__file__))
        target = cwd

        def _makedir(target_dir, sub_dir=None):
            dir = target_dir
            if sub_dir != None:
                dir = path.join(dir, sub_dir)
            (not path.exists(dir)) and mkdir(dir)
            logging.info('Creating %s' % dir)

        if name != '':
            target = path.join(cwd, name)

        maps = json.load(self.app.open_resource('mapaths.json'))

        _makedir(target)
        [_makedir(target, subdir) for subdir in maps['dirs']]

        def _copy_file(fo):
            src_root = basedir
            dest_root = target

            if fo['cwd'] != '':
                src_root = path.join(basedir, fo['cwd'])

            if fo['dest'] != '':
                dest_root = path.join(target, fo['dest'])

            [copy(path.join(src_root, fn), path.join(dest_root, fn)) for fn in fo['src']]

        logging.info('Copying files ...')
        [_copy_file(f) for f in maps['files']]

        asset_content = self.app.open_resource('_assets.yml').read() % {'app': path.basename(target)}
        file(path.join(target, '_assets.yml'), 'w').write(asset_content)

        logging.info('All done! congratulations! Your web has created in %s.' % target)

        self.app.init()
        #ManageAssets(self.app.assets_env).run(['build'])

def create_scripts(app):
    manager = Manager(app)
    manager.add_command("assets", ManageAssets(app.assets_env))
    manager.add_command("build", SiteGenerator(app))
    manager.add_command("new", SkeletonGenerator(app))

    @manager.command
    def serve():
        import SimpleHTTPServer
        import SocketServer
        from os import chdir
        import webbrowser

        PORT = 8000

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

        httpd = SocketServer.TCPServer(("", PORT), Handler)

        print "Freezes static file server now serving on port ", PORT
        chdir('builds')
        webbrowser.open_new_tab('http://localhost:%s' % PORT)
        httpd.serve_forever()

    return manager

