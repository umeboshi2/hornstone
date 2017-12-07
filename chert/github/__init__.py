from github import Github


def make_client(username, password):
    return Github(username, password)


def make_portal(creds):
    mcreds = dict(creds.items('main'))
    return make_client(mcreds['user'], mcreds['password'])
