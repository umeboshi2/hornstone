import os, sys
import hashlib
import cPickle as Pickle
import subprocess


#from useless.base.path import path
from unipath.path import Path as path
from unipath import FILES, DIRS, LINKS

    
def assert_git_directory(directory):
    directory = path(directory)
    here = path.cwd()
    os.chdir(directory)
    cmd = ['git', 'rev-parse']
    subprocess.check_call(cmd)
    os.chdir(here)

def make_key(kdict):
    return '%(method)s-s%(size)d--%(checksum)s' % kdict


def parse_key(keystring):
    method, size, ignore, checksum = keystring.strip().split('-')
    if not size.startswith('s'):
        raise RuntimeError, "Bad size %s" % size
    # strip string and create number for size
    size = int(size[1:])
    return dict(method=method, size=size, checksum=checksum)
