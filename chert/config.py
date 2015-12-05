import os
from ConfigParser import ConfigParser
from StringIO import StringIO


DEFAULT_CONFIG_TEXT = """\
# Configuration file for chert

[main]
# put something here....
"""

default_file = os.path.expanduser('~/.config/chert/chert.ini')
config = ConfigParser()
if not os.path.isfile(default_file):
    dirname = os.path.dirname(default_file)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    print 'Generating default config...'
    config.readfp(StringIO(DEFAULT_CONFIG_TEXT))
    with file(default_file, 'w') as outfile:
        config.write(outfile)

config.read([default_file])
