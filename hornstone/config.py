import os
from configparser import ConfigParser
from io import StringIO


DEFAULT_CONFIG_TEXT = """\
# Configuration file for hornstone

[main]
# put something here....
"""

default_file = os.path.expanduser('~/.config/hornstone/hornstone.ini')
config = ConfigParser()
if not os.path.isfile(default_file):
    dirname = os.path.dirname(default_file)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    print('Generating default config...')
    config.readfp(StringIO(DEFAULT_CONFIG_TEXT))
    with open(default_file, 'w') as outfile:
        config.write(outfile)

config.read([default_file])
