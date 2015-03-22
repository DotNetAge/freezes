"""
Freezes
------------

Transform the plain text or blog to static website.

Links
`````

* `documentation <http://packages.python.org/Freezes>`_
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
DESCRIPTION = README.split('\n')[3]

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
             'layouts/*',
             'seeds/*',
             'static/**/*.*',
             'templates/*.html',
             'templates/*.xml',
             'templates/**/*.*'
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
    url='https://github.com/DotNetAge/freezes',
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
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities']
)
