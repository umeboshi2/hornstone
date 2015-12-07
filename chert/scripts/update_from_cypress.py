#!/usr/bin/env python
import os, sys
import subprocess
import json
import socket

from chert.base import clone_repo, update_mirrored_repo
from chert.base import assert_git_directory, parse_config_lines
from chert.base import WorkingDirectory

from chert.config import config

VERBOSE = True

gitprefix = os.path.expanduser(config.get('gitmirror', 'cypress_prefix'))
reposfile = os.path.expanduser(config.get('gitmirror', 'cypress_repos'))
mirror_path = os.path.expanduser(config.get('gitmirror', 'cypress_mirror_path'))


repos = parse_config_lines(reposfile)

def git_url(prefix, repo):
    return '%s/%s.git' % (prefix, repo)
        

def main(verbose=VERBOSE):
    for repo in repos:
        dest = os.path.join(mirror_path, repo)
        print "DEST", dest
        if not os.path.isdir(dest):
            src = git_url(gitprefix, repo)
            print "Cloning repo", repo, "from", src
            print repo, src, dest
            print 234*'2'
            clone_repo(src, dest, mirror=True, verbose=True)
        else:
            print "Updating repo", repo
            update_mirrored_repo(dest)
        cmd = ['git', '-C', dest, 'gc']
        print "Garbage Collection for", repo
        subprocess.check_call(cmd)
        
