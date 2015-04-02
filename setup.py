"""
Freezes
------------

Transform the plain text or blog to static website.

Links
`````

* `documentation <http://freezes.dotnetage.com>`_
"""

import os
import re
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__),
                       'freezes', '__init__.py')) as init_py:
    VERSION = re.search("VERSION = '([^']+)'", init_py.read()).group(1)

with open('README.rst') as readme_file:
    README = readme_file.read().strip()

PROJECT = README.strip('#').split('\n')[0].strip().split()[0].lower()
DESCRIPTION = "Transform the plain text or blog to static website"

with open('requirements.txt') as reqs_file:
    REQS = reqs_file.read()

setup(
    name='Freezes',
    version=VERSION,
    packages=find_packages(exclude=['tests']),
    install_requires=REQS,
    package_data={
        '': ['*.yml',
             '*.json',
             '*.cfg',
             'layouts/*',
             'seeds/*',
             'static/**/*.*',
             'templates/*.html',
             'templates/*.xml',
             'templates/**/*.*',
             'translations/*.*',
             'translations/zh/LC_MESSAGES/*'

        ]
    },
    entry_points={
        'console_scripts': [
            'freezes=freezes.server:main'
        ],
        'setuptools.installation': [
            'eggsecutable = freezes.server:main'
        ]
    },
    url='http://freezes.dotnetage.com',
    license='BSD',
    author='Ray',
    author_email='csharp2002@hotmail.com',
    description=DESCRIPTION,
    long_description=README,
    zip_safe=False,
    platforms='any',
    keywords=('static', 'flask'),
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities']
)
