from os import path, getcwd


class Config:
    FLATPAGES_MARKDOWN_EXTENSIONS = ['extra', 'nl2br', 'codehilite', 'toc', 'headerid']
    FLATPAGES_EXTENSION = '.md'
    FREEZER_STATIC_IGNORE = ['*.less', '*.coffee', '*.scss']
    TESTING = False
    DEBUG = True
    AUTO_BUILD = True
    ASSETS_DEBUG = False
    CACHE = False

    def __init__(self, app_path=None):

        if app_path is None or (app_path == ''):
            self.APP_PATH = getcwd()
        else:
            self.APP_PATH = app_path

        _app_path = lambda *p: path.join(self.APP_PATH, *p)

        self.FLATPAGES_ROOT = _app_path('pages')
        self.FREEZER_DESTINATION = _app_path('builds')
        self.LOAD_PATH = _app_path('static')
