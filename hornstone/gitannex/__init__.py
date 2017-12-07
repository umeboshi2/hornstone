import os
import pickle as Pickle
from io import StringIO
import subprocess
import json
import socket


from hornstone.base import WorkingDirectory
from hornstone.gitfunc import assert_git_directory

zero_key_old = 'SHA256-s0--e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'  # noqa

zero_key_prefix = 'SHA256E-s0--e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'  # noqa


def run_command(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    if proc.returncode:
        msg = "%s returned %d" % (' '.join(cmd), proc.returncode)
        raise RuntimeError(msg)
    return proc


def get_command_output(cmd):
    proc = run_command(cmd)
    return proc.stdout.read()


def make_key(kdict):
    return '%(method)s-s%(size)d--%(checksum)s' % kdict


def make_old_default_key(size, checksum):
    return 'SHA256-s%d--%s' % (size, checksum)


def make_default_key(size, checksum, ext):
    return 'SHA256E-s%d--%s.%s' % (size, checksum, ext)


def parse_key(keystring):
    method, size, ignore, checksum = keystring.strip().split('-')
    if not size.startswith('s'):
        raise RuntimeError("Bad size %s" % size)
    # strip string and create number for size
    size = int(size[1:])
    return dict(method=method, size=size, checksum=checksum)


def getkey(filepath):
    if filepath.startswith('/'):
        raise RuntimeError("Need relative path")
    cmd = ['git-annex', 'lookupkey', str(filepath)]
    keystring = get_command_output(cmd).strip()
    return parse_key(keystring)


def parse_whereis_topline(topline, filepath):
    whereis_cmd_marker = 'whereis'
    origtop = topline
    if not topline.startswith(whereis_cmd_marker):
        raise RuntimeError("Bad topline: %s" % topline)
    topline = topline[len(whereis_cmd_marker):].strip()
    if not topline.startswith(filepath):
        raise RuntimeError("Bad topline: %s" % topline)
    copies = topline[len(filepath):].strip()
    return dict(copies=copies, origtop=origtop, topline=topline)


def parse_repocopy(line):
    uuid, name = [field.strip() for field in line.split('--')]
    return uuid, name


def make_whereis_proc(output=None):
    cmd = ['git-annex', 'whereis', '--json']
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def make_find_proc(output=None, allrepos=True, inrepos=[]):
    cmd = ['git-annex', 'find', '--json']
    if allrepos:
        cmd += ['--include', '*']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc._cmd_list = cmd
        return proc
    if len(inrepos):
        raise RuntimeError("make --and list of repos for find")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def make_info_proc(fast=True, output=None):
    cmd = ['git-annex', 'info', '--json']
    if fast:
        cmd.append('--fast')
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def annex_info(fast=True):
    proc = make_info_proc(fast=fast)
    if fast:
        proc.wait()
        return json.load(proc.stdout)
    else:
        raise RuntimeError("only --fast currently supported.")


def parse_whereis_command_output(output, verbose_warning=False):
    report_data = dict()
    for line in StringIO(output):
        unicode_decode_error = False
        try:
            filedata = json.loads(line.strip())
        except UnicodeDecodeError:
            unicode_decode_error = True
            if verbose_warning:
                print("Warning converting to unicode:", line.strip())
            line = str(line, errors='replace')
            filedata = json.loads(line.strip())
        filedata['unicode_decode_error'] = unicode_decode_error
        key = filedata['file']
        if key in report_data:
            raise RuntimeError("%s already present." % key)
        report_data[key] = filedata
    return report_data


def make_whereis_data(make_pickle=True):
    main_filename = 'whereis.pickle'
    if os.path.isfile(main_filename):
        return Pickle.load(open(main_filename))
    print("run command")
    cmd = ['git-annex', 'whereis', '--json']
    stdout = subprocess.check_output(cmd)
    print("run command finished")
    report_data = parse_whereis_command_output(stdout)
    Pickle.dump(report_data, open(main_filename, 'w'))
    return report_data


# udata is global uuid repo dictionary
# filedata is git-annex whereis --json output
def update_uuids(udata, filedata):
    original_numkeys = len(list(udata.keys()))
    for item in filedata['whereis']:
        uuid = item['uuid']
        if uuid not in udata:
            description = item['description']
            udata[uuid] = description
    current_numkeys = len(list(udata.keys()))
    if current_numkeys < original_numkeys:
        raise RuntimeError("Bad things happening here")
    if current_numkeys != original_numkeys:
        print("UUID's updated")


def parse_json_line(line, convert_to_unicode=False,
                    verbose_warning=True):
    unicode_decode_error = False
    try:
        data = json.loads(line.strip())
    except UnicodeDecodeError as e:
        if not convert_to_unicode:
            raise UnicodeDecodeError(e)
        unicode_decode_error = True
        if verbose_warning:
            print("Warning converting to unicode:", line)
        line = str(line, errors='replace')
        data = json.loads(line.strip())
    if convert_to_unicode:
        data['unicode_decode_error'] = unicode_decode_error
    return data

# lines is iterable
# either proc.stdout, lines in file, list, etc...


def parse_json_output(lines, counter=None,
                      convert_to_unicode=False,
                      verbose_warning=True,
                      output_to_file=False,
                      output_filename='___INEEDANAME___.output'):
    if output_to_file:
        outfile = open(output_filename, 'w')
    # the while loop will be broken with
    # StopIteration error
    while True:
        try:
            line = next(lines)
            if output_to_file:
                outfile.write(line)
        except StopIteration:
            if output_to_file:
                outfile.close()
            break
        if counter is not None:
            counter += 1
        data = parse_json_line(
            line,
            convert_to_unicode=convert_to_unicode,
            verbose_warning=verbose_warning)
        print("DO SOMETHING WITH DATA", data)


######################################
# more git-annex functions
######################################
class AnnexExistsError(Exception):
    pass


def sync_annex(directory, hosts=None):
    with WorkingDirectory(directory):
        cmd = ['git-annex', 'sync']
        if hosts is not None:
            cmd += hosts
        cmd = ' '.join(cmd)
        subprocess.check_call(cmd, shell=True)


def gitannex_init(directory, name=None):
    assert_git_directory(directory)
    with WorkingDirectory(directory):
        if os.path.isdir('.git/annex'):
            raise AnnexExistsError("annex already appears initialized")
        if name is None:
            name = socket.gethostname()
        cmd = ['git-annex', 'init', name]
        subprocess.check_call(cmd)
    sync_annex(directory)


def _encryption(encryption=None):
    if encryption is None:
        encryption = 'none'
    return encryption


def _init_remote(working_directory, name, rtype, **kwargs):
    initcmd = ['git-annex', 'initremote', name, 'type=%s' % rtype]
    enablecmd = ['git-annex', 'enableremote', name]
    args = ['%s=%s' % (k, v) for k, v in list(kwargs.items())]
    initcmd += args
    # print "INITCMD", initcmd
    config_marker = '[remote "%s"]' % name
    with WorkingDirectory(working_directory):
        if config_marker not in open('.git/config').read():
            retcode = subprocess.call(initcmd)
            if retcode:
                print("INITREMOTE failed, attempt enable")
                subprocess.call(enablecmd)


def init_dir_remote(working_directory, name, directory, encryption=None):
    kw = dict(encryption=_encryption(encryption), directory=directory)
    _init_remote(working_directory, name, 'directory', **kw)


def init_rsync_remote(working_directory, name, rsyncurl, encryption=None):
    kw = dict(encryption=_encryption(encryption),
              rsyncurl=rsyncurl)
    _init_remote(working_directory, name, 'rsync', **kw)
