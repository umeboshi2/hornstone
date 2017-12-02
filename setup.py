from setuptools import setup, find_packages
import sys, os

version = '0.0'

requires = [
    'SQLAlchemy',
    'psycopg2',        # dbapi for postgresql
    'robobrowser',
    'requests',
    'beautifulsoup4',
    'lxml',
    'transaction',     # I am not sure if I should use this or not
    'rarfile',
    'unipath',
    'PyGithub',
    'gitpython',
]

setup(name='chert',
      version=version,
      description="A bunch of rocks",
      long_description="""\
A bunch of rocks""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Joseph Rawson',
      author_email='joseph.rawson.works@gmail.com',
      url='https://github.com/umeboshi2/chert',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      """,
      )
