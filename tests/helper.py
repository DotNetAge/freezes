from os import mkdir, path, walk
from shutil import copy, rmtree
from freezes.server import create_app
from freezes.views import create_views
from freezes.pagext import extend_pages
from freezes.config import Config


app_name = 'test_app'
test_app_path = path.join(path.dirname(__file__), app_name)
src_app_path = path.join(path.dirname(path.dirname(__file__)), 'freezes')


def copy_templates(src, target):
    """Copy all template files from freezes src code folder to test folder.
    :param src:
    :param target:
    :return:
    """
    base_path = path.join(target, 'templates')
    layouts = path.join(base_path, 'layouts')

    rmtree(base_path)
    mkdir(base_path)
    mkdir(layouts)
    mkdir(path.join(base_path, 'includes'))

    for root, dirs, files in walk(path.join(src, 'layouts')):
        for file in files:
            src_file = path.join(root, file)
            if file == '404.html':
                copy(src_file, path.join(base_path, '404.html'))
            else:
                copy(src_file, path.join(layouts, file))


def clean_builds():
    build_path = path.join(test_app_path, 'builds')
    if path.exists(build_path):
        rmtree(build_path)


def clean_pages():
    page_path = path.join(test_app_path, 'pages')
    if path.exists(page_path):
        rmtree(page_path)
    mkdir(page_path)


def clean():
    if path.exists(test_app_path):
        rmtree(test_app_path)


def create_test_app():
    test_config = Config(test_app_path)
    test_config.TESTING=True
    test_config.ASSETS_DEBUG = True
    _app = create_app(test_config)
    create_views(app_name, _app)
    extend_pages(app_name)
    return _app


def init_test_case(test_case, test_app):
    test_app.init()
    test_case.app_context = test_app.app_context()
    test_case.app_context.push()
    test_case.app = test_app.test_client()
    # copy_templates(src_app_path, test_app_path)

#
# def init_script_test_case(test_case, new_app='test_new_app'):
# setup_target_path = path.join(path.dirname(__file__), new_app)
#
# test_config = Config(setup_target_path)
# test_config.ASSETS_DEBUG = True
#
#     _app = create_app(test_config)
#     create_views(new_app, _app)
#     extend_pages(new_app)
#
#     if path.exists(setup_target_path):
#         rmtree(setup_target_path)
#     test_case.app = _app
