#!/usr/bin/env python
import os, sys
from ConfigParser import ConfigParser
import cPickle as Pickle

from pygithub3 import Github


def make_portal(creds):
    mcreds = dict(creds.items('main'))
    return Github(login=mcreds['user'], password=mcreds['password'])
    

creds = ConfigParser()
creds.read(['.creds'])

gh = make_portal(creds)
user = gh.users.get()

repos_filename = 'repos.pickle'
if os.path.exists(repos_filename):
    repos = Pickle.load(file(repos_filename))
else:
    result = gh.repos.list()
    repos = result.all()
    with file(repos_filename, 'w') as outfile:
        Pickle.dump(repos, outfile)
        
