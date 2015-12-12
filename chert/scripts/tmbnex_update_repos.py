#!/usr/bin/env python
import os, sys
import subprocess
import json
import socket

from chert.base import clone_repo, update_repo
from chert.base import assert_git_directory
from chert.base import WorkingDirectory
from chert.base import parse_config_lines

from chert.gitannex import sync_annex, gitannex_init
from chert.gitannex import init_rsync_remote

from chert.config import config


reposfile = os.path.expanduser(config.get('tmbnex', 'reposlist'))

repos = parse_config_lines(reposfile)

annexes = os.path.expanduser(config.get('tmbnex', 'local_annexdir'))

origin = config.get('tmbnex', 'origin_prefix')


rsync_reponame = config.get('tmbnex', 'rsync_reponame')
rsync_url = config.get('tmbnex', 'rsync_url')


def copy_to_rsync_repo(directory):
    with WorkingDirectory(directory) as wd:
        cmd = ['git-annex', 'copy', '--to', rsync_reponame]
        subprocess.check_call(cmd)
        

def main():
    for repo in repos:
        dest = os.path.join(annexes, repo)
        print "DEST", dest
        if not os.path.isdir(dest):
            src = os.path.join(origin, repo)
            print "Cloning repo", repo
            print origin, repo, src, dest
            print 234*'2'
            clone_repo(src, dest)
            gitannex_init(dest)
        else:
            sync_annex(dest)
        init_rsync_remote(dest, rsync_reponame, rsync_url)
        if 'COLLECT_THE_GARBAGE' in os.environ:
            cmd = ['git', '-C', dest, 'gc']
            print "Garbage Collection for", repo
            subprocess.check_call(cmd)
        
