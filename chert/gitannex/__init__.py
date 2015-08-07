import os, sys
import hashlib
import cPickle as Pickle
from cStringIO import StringIO
import subprocess
import json


#from useless.base.path import path
from unipath.path import Path as path
from unipath import FILES, DIRS, LINKS

def run_command(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
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


def whereisorig(filepath):
    cmd = ['git-annex', 'whereis', str(filepath)]
    proc = run_command(cmd)
    data = dict()
    lines = [l.strip() for l in proc.stdout.readlines()]
    lastline = lines[-1]
    if lastline != 'ok':
        raise RuntimeError, "Problem with %s" % filepath
    topline = lines[0]
    while topline == '(Recording state in git...)':
        lines = lines[1:]
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

def whereis(filepath):
    if os.path.isdir(filepath):
        raise RuntimeError, "%s is a directory." % filepath
    cmd = ['git-annex', 'whereis', '--json', filepath]
    output = subprocess.check_output(cmd)
    return json.loads(output.strip())

    
def parse_whereis_command_output(output, verbose_warning=False):
    report_data = dict()
    for line in StringIO(output):
        try:
            filedata = json.loads(line.strip())
        except UnicodeDecodeError:
            if verbose_warning:
                print "Warning converting to unicode:", line.strip()
            line = unicode(line, errors='replace')
            filedata = json.loads(line.strip())
        key = filedata['file']
        if key in report_data:
            raise RuntimeError, "%s already present." % key
        report_data[key] = filedata
    return report_data

def make_whereis_data(make_pickle=True):
    main_filename = 'whereis.pickle'
    if os.path.isfile(main_filename):
        return Pickle.load(file(main_filename))
    print "run command"
    cmd = ['git-annex', 'whereis', '--json']
    stdout = subprocess.check_output(cmd)
    print "run command finished"
    report_data = parse_whereis_command_output(stdout)
    Pickle.dump(report_data, file(main_filename, 'w'))
    return report_data



# udata is global uuid repo dictionary
# filedata is git-annex whereis --json output
def update_uuids(udata, filedata):
    changed = False
    original_numkeys = len(udata.keys())
    for item in filedata['whereis']:
        uuid = item['uuid']
        if uuid not in udata:
            description = item['description']
            udata[uuid] = description
    current_numkeys = len(udata.keys())
    if current_numkeys < original_numkeys:
        raise RuntimeError, "Bad things happening here"
    if current_numkeys != original_numkeys:
        print "UUID's updated"
        
