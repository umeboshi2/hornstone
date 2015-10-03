#!/usr/bin/env python
import os, sys
from ConfigParser import ConfigParser
import cPickle as Pickle

from github import Github



def make_client(username, password):
    return Github(username, password)

def make_portal(creds):
    mcreds = dict(creds.items('main'))
    return make_client(mcreds['user'], mcreds['password'])
    
