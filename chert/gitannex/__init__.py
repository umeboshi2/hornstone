import os, sys
import hashlib
import cPickle as Pickle
import subprocess


#from useless.base.path import path
from unipath.path import Path as path
from unipath import FILES, DIRS, LINKS

def run_command(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    proc.wait()
    if proc.returncode:
        msg = "%s returned %d" % (' '.join(cmd), proc.returncode)
        raise RuntimeError, msg
    return proc

def get_command_output(cmd):
    proc = run_command(cmd)
    return proc.stdout.read()


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

def getkey(filepath):
    if filepath.startswith('/'):
        raise RuntimeError, "Need relative path"
    cmd = ['git-annex', 'lookupkey', str(filepath)]
    keystring = get_command_output(cmd).strip()
    return parse_key(keystring)

def parse_whereis_topline(topline, filepath):
    whereis_cmd_marker = 'whereis'
    origtop = topline
    if not topline.startswith(whereis_cmd_marker):
        raise RuntimeError, "Bad topline: %s" % topline
    topline = topline[len(whereis_cmd_marker):].strip()
    if not topline.startswith(filepath):
        raise RuntimeError, "Bad topline: %s" % topline    
    copies = topline[len(filepath):].strip()
    return dict(copies=copies, origtop=origtop, topline=topline)

def parse_repocopy(line):
    uuid, name = [field.strip() for field in line.split('--')]
    return uuid, name


def whereis(filepath):
    cmd = ['git-annex', 'whereis', str(filepath)]
    proc = run_command(cmd)
    data = dict()
    lines = [l.strip() for l in proc.stdout.readlines()]
    lastline = lines[-1]
    if lastline != 'ok':
        raise RuntimeError, "Problem with %s" % filepath
    topline = lines[0]
    parsed_topline = parse_whereis_topline(topline, filepath)
    reposlice = lines[1:-1]
    repo_copies = [parse_repocopy(l) for l in reposlice]
    data = dict(lines=lines,
                lastline=lastline,
                reposlice=reposlice,
                repo_copies=repo_copies,
                filepath=filepath)
    data.update(parsed_topline)
    return data

def make_whereis_report():
    pass

