#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'more-itertools',
    'SQLAlchemy',
    'psycopg2',        # dbapi for postgresql
    'transaction',
    'sqlalchemy-utils',
    'robobrowser',
    'requests',
    'beautifulsoup4',
    'lxml',
    'rarfile',
    'unipath',
    'PyGithub',
    'gitpython',
    'passlib',
]
setup_requirements = [
    'pytest-runner',
    # TODO(umeboshi2): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]


setup(
    name='hornstone',
    version='0.1.23',
    description="A bunch of rocks",
    long_description=readme,
    author="Joseph Rawson",
    author_email='joseph.rawson.works@gmail.com',
    url='https://github.com/umeboshi2/hornstone',
    license='Public Domain',
    packages=find_packages(include=['hornstone', 'hornstone.*']),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='hornstone',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
