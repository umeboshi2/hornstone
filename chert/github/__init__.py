#!/usr/bin/env python
import os, sys
from ConfigParser import ConfigParser
import cPickle as Pickle

from github import Github


def make_portal(creds):
    mcreds = dict(creds.items('main'))
    return Github(mcreds['user'], mcreds['password'])
    

