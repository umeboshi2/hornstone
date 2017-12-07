import os
import subprocess

from unipath.path import Path as path
from git import Repo

from .githubdb import GitHubUser, GitHubRepo


class RepoManager(object):
    def __init__(self, session, user_id):
        self.session = session
        self.ghclient = None
        self.repo_path = None
        self.user = session.query(GitHubUser).get(user_id)

    def set_repo_path(self, repo_path):
        repo_path = path(repo_path)
        if not repo_path.isdir():
            raise RuntimeError("%s doesn't exist." % repo_path)
        self.repo_path = repo_path

    def set_github_client(self, ghclient):
        self.ghclient = ghclient

    def get_my_repos(self):
        user_id = self.user.id
        q = self.session.query(GitHubRepo).filter_by(owner_id=user_id)
        return q.all()

    def local_reponame(self, dbrepo):
        reponame = dbrepo.full_name
        if not reponame.startswith(self.user.login):
            reponame = os.path.join('others', dbrepo.name)
        reponame = os.path.join(self.repo_path, '%s.git' % reponame)
        return reponame

    def local_repo_exists(self, dbrepo):
        return os.path.isdir(self.local_reponame(dbrepo))

    def destroy_repo(self, dbrepo):
        if self.local_repo_exists(dbrepo):
            dirname = self.local_reponame(dbrepo)
            cmd = ['rm', '-fr', str(dirname)]
            subprocess.check_call(cmd)

    def clone_repo(self, dbrepo, reponame=None, size_limit=None):
        if size_limit is not None:
            if dbrepo.size > size_limit:
                print("%s too big." % dbrepo.full_name, dbrepo.size)
                return
        clone_url = dbrepo.pickle.clone_url
        if reponame is None:
            reponame = self.local_reponame(dbrepo)
        repo = Repo.clone_from(clone_url, reponame, bare=True)
        return repo

    def local_repo(self, dbrepo):
        return Repo(self.local_reponame(dbrepo))

    def _clone_repolist(self, repolist, size_limit=None):
        for repo in repolist:
            reponame = self.local_reponame(repo)
            if not os.path.isdir(reponame):
                self.clone_repo(repo,
                                reponame=reponame,
                                size_limit=size_limit)

    def clone_my_repos(self, size_limit=1000):
        my_repos = self.get_my_repos()
        self._clone_repolist(my_repos, size_limit=size_limit)

    def clone_other_repos(self, size_limit=1000):
        query = self.session.query(GitHubRepo)
        others = query.filter(GitHubRepo.owner_id != self.user.id)
        self._clone_repolist(others, size_limit=size_limit)

    def update_from_github(self):
        pass
