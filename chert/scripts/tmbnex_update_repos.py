#!/usr/bin/env python
import os, sys
import subprocess
import json
import socket

from chert.base import clone_repo, update_repo
from chert.base import assert_git_directory
from chert.base import WorkingDirectory

from chert.config import config

reposfile = os.path.expanduser(config.get('tmbnex', 'reposlist'))

repos = [line.strip() for line in file(reposfile)
         if line.strip() and not line.strip().startswith('#')]

annexes = os.path.expanduser(config.get('tmbnex', 'local_annexdir'))

origin = config.get('tmbnex', 'origin_prefix')


    
def sync_annex(directory, hosts=None):
    with WorkingDirectory(directory) as wd:
        cmd = ['git-annex', 'sync']
        if hosts is not None:
            cmd += hosts
        cmd = ' '.join(cmd)
        subprocess.check_call(cmd, shell=True)

def init_mybook_remote(directory):
    with WorkingDirectory(directory) as wd:
        initcmd = ['git-annex', 'initremote', 'mybook', 'type=rsync',
               'rsyncurl=mybooklive:/shares/tbannex', 'encryption=none',]
        
        enablecmd = ['git-annex', 'enableremote', 'mybook',
                     'rsyncurl=mybooklive:/shares/tbannex']
        if 'mybooklive:/shares/tbannex' not in file('.git/config').read():
                retcode = subprocess.call(initcmd)
                if retcode:
                    subprocess.call(enablecmd)
            
    
def gitannex_init(directory, name=None):
    assert_git_directory(directory)
    with WorkingDirectory(directory) as wd:
        if os.path.isdir('.git/annex'):
            raise RuntimeError, "already appears initialized"
        if name is None:
            name = socket.gethostname()
        cmd = ['git-annex', 'init', name]
        subprocess.check_call(cmd)
    sync_annex(directory)

def copy_to_mybook(directory):
    with WorkingDirectory(directory) as wd:
        cmd = ['git-annex', 'copy', '--to', 'mybook']
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
        init_mybook_remote(dest)
    
