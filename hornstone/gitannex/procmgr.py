import os
import subprocess
import json


class GitAnnexProcManager(object):
    def __init__(self, annex_directory):
        if not os.path.isdir(annex_directory):
            raise RuntimeError("No such directory %s" % annex_directory)
        self.annex_directory = annex_directory

    def make_proc(self, cmd, stdout=subprocess.PIPE):
        proc = subprocess.Popen(
            cmd, stdout=stdout, cwd=self.annex_directory)
        proc._cmd_list = cmd
        return proc

    def make_whereis_proc(self):
        cmd = ['git-annex', 'whereis', '--json']
        return self.make_proc(cmd)

    def make_find_proc(self, allrepos=True, inrepos=None):
        if inrepos is not None and len(inrepos):
            raise RuntimeError("make --and list of repos for find")
        cmd = ['git-annex', 'find', '--json']
        if allrepos:
            cmd += ['--include', '*']
        return self.make_proc(cmd)

    def make_info_proc(self, fast=True):
        cmd = ['git-annex', 'info', '--json']
        if fast:
            cmd.append('--fast')
        return self.make_proc(cmd)

    def get_annex_info(self):
        proc = self.make_info_proc(fast=True)
        proc.wait()
        return json.load(proc.stdout)
