import os
import json
import subprocess

from unipath.path import Path as path


def assert_git_directory(directory):
    directory = path(directory)
    assert directory.isdir()
    cmd = ['git', '-C', directory, 'rev-parse']
    subprocess.check_call(cmd)


def clone_repo(uri, dest, branch=None, quiet=True, bare=False,
               mirror=False, verbose=False):
    cmd = ['git', 'clone']
    if quiet:
        cmd.append('--quiet')
    if branch is not None:
        cmd += ['--branch', branch]
    if bare:
        cmd.append('--bare')
    if mirror:
        cmd.append('--mirror')
    cmd += [uri, dest]
    if verbose:
        print("Clone command: %s" % ' '.join(cmd))
    subprocess.check_call(cmd)


def fetch_all(directory, quiet=False):
    assert_git_directory(directory)
    prefix = ['git', '-C', directory]
    cmd = prefix + ['fetch', '--all']
    subprocess.check_call(cmd)


def update_repo(directory, quiet=False, all=True):
    assert_git_directory(directory)
    assert os.path.isdir(directory)
    prefix = ['git', '-C', directory]
    current_sha_cmd = prefix + ['rev-parse', 'HEAD']
    current_sha = subprocess.check_output(current_sha_cmd).strip()
    cmd = prefix + ['fetch']
    if quiet:
        cmd.append('--quiet')
    if all:
        cmd.append('--all')
    upstream_sha_cmd = prefix + ['rev-parse', 'FETCH_HEAD']
    upstream_sha = subprocess.check_output(upstream_sha_cmd).strip()
    if current_sha != upstream_sha:
        subprocess.check_call(prefix + ['merge', upstream_sha])


def update_mirrored_repo(directory):
    cmd = ['git', '-C', directory, 'remote', 'update']
    subprocess.check_call(cmd)


# FIXME - this is git-annex
def check_remote_present(directory, name):
    assert_git_directory(directory)
    oldpwd = os.getcwd()
    os.chdir(directory)
    cmd = ['git-annex', 'info', '--fast', '--json', name]
    out = subprocess.check_output(cmd)
    os.chdir(oldpwd)
    return json.loads(out)
