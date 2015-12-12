#!/usr/bin/env python
import os, sys
import subprocess
import json
import gzip
import argparse

from chert.base import WorkingDirectory
from chert.gitannex import gitannex_init, sync_annex
from chert.gitannex import AnnexExistsError
from chert.gitannex import init_rsync_remote

from chert.config import config


def get_posts_and_blogname(postsfile):
    print "POSTSFILE", postsfile
    if not postsfile.endswith('.json.gz'):
        raise RuntimeError, "bad file %s" % postsfile
    basename = os.path.basename(postsfile)
    blogname = basename.split('.json')[0]
    print "BLOGNAME", blogname, config
    posts = json.load(gzip.GzipFile(postsfile))
    return blogname, posts

def create_annex_Orig(annexdir):
    if not os.path.isdir(annexdir):
        cmd = ['git', 'init', annexdir]
        subprocess.check_call(cmd)

    with WorkingDirectory(annexdir) as wd:
        print "CWD", os.getcwd()
        if not os.path.isdir('.git/annex'):
            print "init git-annex"
            cmd = ['git-annex', 'init']
            subprocess.check_call(cmd)
    
def create_annex(annexdir):
    if not os.path.isdir(annexdir):
        cmd = ['git', 'init', annexdir]
        subprocess.check_call(cmd)
    try:
        gitannex_init(directory, name='origin')
    except AnnexExistsError:
        print "Annex already initialized"
    

def add_post_urls(posts):
    for filename, url in posts.items():
        if not os.path.islink(filename):
            cmd = ['git-annex', 'addurl', '--file', filename, url]
            subprocess.call(cmd)
        else:
            print "File exists", filename


def main():
    annex_prefix = config.get('tmbnex', 'create_parent_path')
    annex_prefix = os.path.expanduser(annex_prefix)
    parser = argparse.ArgumentParser()
    parser.add_argument('postsfile')
    
    args = parser.parse_args()

    blogname, posts = get_posts_and_blogname(args.postsfile)
    annexdir = os.path.join(annex_prefix, blogname)
    create_annex(annexdir)
    with WorkingDirectory(annexdir) as wd:
        add_post_urls(posts)
        subprocess.check_call(['git-annex', 'sync'])
