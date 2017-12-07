# column types
from .githubdb import GitHubUser, GitHubRepo


class NoNamedUserError(Exception):
    pass


user_attributes = [
    'id',
    'login',
    'avatar_url',
    'gravatar_id',
    'url',
    'html_url',
    'followers_url',
    'following_url',
    'gists_url',
    'starred_url',
    'subscriptions_url',
    'organizations_url',
    'repos_url',
    'events_url',
    'received_events_url',
    'type',
    'name',
    'company',
    'blog',
    'location',
    'email',
    'hireable',
    'bio',
    'public_repos',
    'public_gists',
    'followers',
    'following',
]


repo_attributes = [
    'id',
    'name',
    'full_name',
    'description',
    'private',
    'fork',
    'default_branch',
    'homepage',
    'url',
    'html_url',
    'has_issues',
    'has_wiki',
    'has_downloads',
    'size',
    'forks_count',
    'stargazers_count',
    'open_issues_count',
    'pushed_at',
]


def _make_dbobject(robj, dbclass, attributes):
    dbobj = dbclass()
    for attr in attributes:
        setattr(dbobj, attr, getattr(robj, attr))
    for attr in ['created_at', 'updated_at']:
        dbattr = '%s_gh' % attr
        setattr(dbobj, dbattr, getattr(robj, attr))
    dbobj.pickle = robj
    return dbobj


def make_dbuser(user):
    return _make_dbobject(user, GitHubUser, user_attributes)


def make_dbrepo(repo):
    dbrepo = _make_dbobject(repo, GitHubRepo, repo_attributes)
    dbrepo.owner_id = repo.owner.id
    return dbrepo


def add_dbuser(session, dbuser):
    session.add(dbuser)
    return session.merge(dbuser)

# if repo_owner is not None, it is repo.owner from github


def add_dbrepo(session, dbrepo, repo_owner=None, verbose=False):
    owner = session.query(GitHubUser).get(dbrepo.owner_id)
    if owner is None:
        if repo_owner is None:
            msg = "No user in database owning repo %s" % dbrepo.full_name
            raise NoNamedUserError(msg)
        if verbose:
            print("Add new user", repo_owner.login)
        dbuser = make_dbuser(repo_owner)
        dbuser = add_dbuser(session, dbuser)
    session.add(dbrepo)
    return session.merge(dbrepo)


def _import_repos(session, repolist, verbose=False):
    for repo in repolist:
        dbrepo = session.query(GitHubRepo).get(repo.id)
        if dbrepo is None:
            if verbose:
                print("Add new repo", repo.full_name)
            dbrepo = make_dbrepo(repo)
            dbrepo = add_dbrepo(session, dbrepo, repo_owner=repo.owner,
                                verbose=verbose)


def import_basic_data(session, ghub, commit=False, verbose=False):
    user = ghub.get_user()
    user_id = user.id
    dbuser = session.query(GitHubUser).get(user_id)
    if dbuser is None:
        if verbose:
            print("Add main user", user.login)
        dbuser = make_dbuser(user)
        session.add(dbuser)
    # import main repos
    _import_repos(session, user.get_repos(), verbose=verbose)
    # import starred repos
    _import_repos(session, user.get_starred(), verbose=verbose)
    if commit:
        if verbose:
            print("Committing Data...")
        session.commit()
