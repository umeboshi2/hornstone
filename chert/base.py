import os
import hashlib
import subprocess
import json

from unipath.path import Path as path
from unipath import FILES, DIRS, LINKS
from git import Repo


#http://code.activestate.com/recipes/576620-changedirectory-context-manager/
class WorkingDirectory(object):
    def __init__(self, directory):
        self._dir = directory
        self._cwd = os.getcwd()
        self._pwd = self._cwd

    @property
    def current(self):
        return self._cwd

    @property
    def previous(self):
        return self._pwd

    @property
    def relative(self):
        c = self._cwd.split(os.path.sep)
        p = self._pwd.split(os.path.sep)
        l = min(len(c), len(p))
        i = 0
        while i < l and c[i] == p[i]:
            i += 1
        return os.path.normpath(os.path.join(*(['.'] + (['..'] * (len(c) - i)) + p[i:])))

    def __enter__(self):
        self._pwd = self._cwd
        os.chdir(self._dir)
        self._cwd = os.getcwd()
        return self

    def __exit__(self, *args):
        os.chdir(self._pwd)
        self._cwd = self._pwd
        

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def get_sha256sum_orig(fileobj):
    s = hashlib.new('sha256')
    while True:
        block = fileobj.read(4096)
        if not block:
            break
        s.update(block)
    return s.hexdigest()

def get_sha256sum(fileobj):
    s = hashlib.new('sha256')
    block = fileobj.read(4096)
    while block:
        s.update(block)
        block = fileobj.read(4096)
    return s.hexdigest()

def get_sha256sum_string(string):
    s = hashlib.new('sha256')
    s.update(string)
    return s.hexdigest()

def remove_trailing_slash(pathname):
    while pathname.endswith('/'):
        pathname = pathname[:-1]
    return pathname

def assert_git_directory(directory):
    directory = path(directory)
    assert directory.isdir()
    cmd = ['git', '-C', directory, 'rev-parse']
    subprocess.check_call(cmd)

def clone_repo(uri, dest, branch=None, quiet=True):
    cmd = ['git', 'clone']
    if quiet:
        cmd.append('--quiet')
    if branch is not None:
        cmd += ['--branch', branch]
    cmd += [uri, dest]
    subprocess.check_call(cmd)

def update_repo(directory):
    assert_git_directory(directory)
    assert os.path.isdir(directory)
    prefix = ['git', '-C', directory]
    current_sha_cmd = prefix + ['rev-parse', 'HEAD']
    current_sha = subprocess.check_output(current_sha_cmd).strip()
    subprocess.check_call(prefix + ['fetch', '--quiet'])
    upstream_sha_cmd = prefix + ['rev-parse', 'FETCH_HEAD']
    upstream_sha = subprocess.check_output(upstream_sha_cmd).strip()
    if current_sha != upstream_sha:
        subprocess.check_call(prefix + ['merge', upstream_sha])
    

def check_remote_present(directory, name):
    assert_git_directory(directory)
    oldpwd = os.getcwd()
    os.chdir(directory)
    cmd = ['git-annex', 'info', '--fast', '--json', name]
    out = subprocess.check_output(cmd)
    os.chdir(oldpwd)
    return json.loads(out)

def add_rsync_remote(directory, name, url):
    assert_git_directory(directory)
    oldpwd = os.getcwd()
    os.chdir(directory)
    #cmd = ['git-annex', 'info', '--fast', '--json', name]
    
    out = subprocess.check_output(cmd)
    os.chdir(oldpwd)
    return json.loads(out)
    
