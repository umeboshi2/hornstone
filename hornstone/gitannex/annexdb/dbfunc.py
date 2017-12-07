import os
import json
from datetime import datetime
import tempfile

from sqlalchemy import func
from sqlalchemy import distinct
from sqlalchemy import desc

from sqlalchemy.orm.exc import NoResultFound

from hornstone.base import remove_trailing_slash

from hornstone import gitannex

from hornstone.gitannex.annexdb.schema import AnnexKey, AnnexFile
from hornstone.gitannex.annexdb.schema import RepoFile


dt_isoformat = '%Y-%m-%dT%H:%M:%S'


def make_keyid_lookup_dict(session):
    data = dict()
    for dbk in session.query(AnnexKey).all():
        data[dbk.name] = dbk.id
    return data


def count_annex_key_func():
    return func.count(AnnexFile.key_id).label('key_count')


# this returns a tuple of two integers
# (key_id, count(key_id))
def make_dupe_count_query(session):
    cf = count_annex_key_func()
    cq = session.query(AnnexFile.key_id, cf).group_by(AnnexFile.key_id)
    cq = cq.subquery()
    return session.query(cq).filter(cq.c.key_count > 1)


def make_dupefile_query(session):
    sq = make_dupe_count_query(session).subquery()
    q = session.query(AnnexFile, sq).filter(AnnexFile.key_id == sq.c.key_id)
    q = q.order_by(AnnexFile.key_id, AnnexFile.name)
    return q


def make_dupedict(dupeqry):
    dupedict = dict()
    for df in dupeqry:
        annex_key = df.key.name
        if annex_key not in dupedict:
            dupedict[annex_key] = list()
        dupedict[annex_key].append(df)
    return dupedict


def compare_two_dirs(session, dir_one, dir_two):
    dir_one = remove_trailing_slash(dir_one)
    dir_two = remove_trailing_slash(dir_two)
    dfq = make_dupefile_query(session)
    sets_of_interest = dict()
    current_set = dict()
    dupedict = make_dupedict(dfq)
    for annex_key in dupedict:
        dir_one_present = False
        dir_two_present = False
        current_set = dict()
        current_set[annex_key] = list()
        for dfile in dupedict[annex_key]:
            current_set.append(dfile)
            if dfile.name.startswith(dir_one):
                dir_one_present = True
            if dfile.name.startswith(dir_two):
                dir_two_present = True
        if dir_one_present and dir_two_present:
            if len(dupedict[annex_key]) == 2:
                if annex_key not in sets_of_interest:
                    sets_of_interest.update(current_set)
    return sets_of_interest

# this will return paths that are not
# necessarily under the parent, but one
# of the paths in the set of duplicates
# will be under the parent.


def dupekeys_under_parent(session, parent_directory):
    parent_directory = remove_trailing_slash(parent_directory)
    dfq = make_dupefile_query(session)
    psq = dfq.filter(AnnexFile.name.like('%s/%%' %
                                         parent_directory)).subquery()
    key_query = session.query(distinct(psq.c.key_id))
    return key_query


def dupefiles_under_parent(session, parent_directory):
    keys = dupekeys_under_parent(session, parent_directory)
    q = session.query(AnnexFile).filter(AnnexFile.key_id.in_(keys))
    return q.order_by(AnnexFile.key_id, AnnexFile.name)


def zero_bytesize_query(session):
    return session.query(AnnexFile).filter_by(bytesize=0)


def largest_files_query(session):
    return session.query(AnnexFile).order_by(desc(AnnexFile.bytesize))


################################
# from make-find-database.py
################################

def get_find_data(session,
                  auto_convert_unicode=False,
                  verbose_warning=True,
                  output_to_file=False,
                  output_filename='find.output'):
    proc = gitannex.make_find_proc()
    count = 0
    if output_to_file:
        outfile = open(output_filename, 'w')
    while proc.returncode is None:
        try:
            line = next(proc.stdout)
            if output_to_file:
                outfile.write(line)
        except StopIteration:
            if output_to_file:
                outfile.close()
            break
        count += 1


def make_find_output():
    ignore, filename = tempfile.mkstemp(prefix='gitannex-find-output-')
    get_find_data('ignore',
                  auto_convert_unicode=True,
                  output_to_file=True,
                  output_filename=filename)
    return filename


def make_whereis_output():
    ignore, filename = tempfile.mkstemp(prefix='gitannex-whereis-output-')
    proc = gitannex.make_whereis_proc()
    count = 0
    outfile = open(filename, 'w')
    while proc.returncode is None:
        try:
            line = next(proc.stdout)
            outfile.write(line)
        except StopIteration:
            outfile.close()
            break
        count += 1
    return filename


def parse_whereis_line(session, line, repoids, convert_to_unicode=True,
                       verbose_warning=True):
    try:
        data = json.loads(line.strip())
    except UnicodeDecodeError as e:
        if not convert_to_unicode:
            raise UnicodeDecodeError(e)
        if verbose_warning:
            print("Warning converting to unicode", line.strip())
        line = str(line, errors='replace')
        data = json.loads(line.strip())
    f = session.query(AnnexFile).filter_by(name=data['file']).one()
    for wdata in data['whereis']:
        uuid = wdata['uuid']
        w = RepoFile()
        w.file_id = f.id
        w.repo_id = repoids[uuid]
        session.add(w)


def parse_whereis_cmd(session, repoids, convert_to_unicode=True,
                      verbose_warning=True):
    proc = gitannex.make_whereis_proc()
    count = 0
    while proc.returncode is None:
        try:
            line = next(proc.stdout)
        except StopIteration:
            break
        parse_whereis_line(session, line, repoids,
                           convert_to_unicode=convert_to_unicode,
                           verbose_warning=verbose_warning)
        count += 1
        if not count % 5000:
            print("committing at count %d" % count)
            session.commit()
    if proc.returncode:
        raise RuntimeError("command returned %d" % proc.returncode)
    session.commit()


def initialize_annex_keys(session, find_output_filename):
    filename = find_output_filename
    keys = set()
    with open(filename) as infile:
        while True:
            try:
                line = next(infile)
            except StopIteration:
                break
            data = gitannex.parse_json_line(
                line,
                convert_to_unicode=True,
                verbose_warning=True)
            keys.add(data['key'])
    for k in keys:
        dbk = AnnexKey()
        dbk.name = k
        session.add(dbk)
    print("added %d keys" % len(keys))
    print(datetime.now())
    session.commit()
    print("successful commit", datetime.now())


def _add_annexfile_attributes_common(dbobj, data):
    dbobj.name = data['file']
    for att in ['backend', 'bytesize', 'humansize',
                'keyname', 'hashdirlower', 'hashdirmixed',
                'unicode_decode_error']:
        setattr(dbobj, att, data[att])
        if data['mtime'] != 'unknown':
            raise RuntimeError("Parse time?")


def _add_annexfile_attributes(keylookup, dbobj, data):
    key = data['key']
    try:
        dbobj.key_id = keylookup[key]
    except KeyError:
        raise KeyError("Unknown key %s" % data)
    _add_annexfile_attributes_common(dbobj, data)


def _add_new_annexfile_attributes(key_id, dbobj, data):
    dbobj.key_id = key_id
    _add_annexfile_attributes_common(dbobj, data)


def add_file_to_database(session, keylookup, filedata,
                         commit=False):
    dbobj = AnnexFile()
    _add_annexfile_attributes(keylookup, dbobj, filedata)
    session.add(dbobj)


def add_files(session, keylookup, find_output_filename):
    with open(find_output_filename) as infile:
        count = 0
        current = datetime.now()
        while True:
            try:
                line = next(infile)
                count += 1
            except StopIteration:
                break
            data = gitannex.parse_json_line(
                line,
                convert_to_unicode=True,
                verbose_warning=True)
            add_file_to_database(session, keylookup, data)
            if not count % 5000:
                print("Committing %d files" % count)
                now = datetime.now()
                print("Diff", now - current)
                current = now
                session.commit()
        print("%d files added." % count)
        session.commit()
        print(datetime.now())


def add_new_file_to_database(session, filedata,
                             commit=False):
    key = filedata['key']
    try:
        keyobj = session.query(AnnexKey).filter_by(name=key).one()
    except NoResultFound:
        keyobj = AnnexKey()
        keyobj.name = key
        session.add(keyobj)
        keyobj = session.merge(keyobj)
    dbobj = AnnexFile()
    _add_new_annexfile_attributes(keyobj.id, dbobj, filedata)
    session.add(dbobj)


def add_new_files(session, keylookup, newfiles):
    count = 0
    current = datetime.now()
    for data in newfiles:
        count += 1
        add_new_file_to_database(session, data)
        if not count % 5000:
            print("Committing %d files" % count)
            now = datetime.now()
            print("Diff", now - current)
            current = now
            session.commit()
    print("%d files added." % count)
    session.commit()
    print(datetime.now())


def populate_whereis(session, repoids):
    print("populating whereis info")
    parse_whereis_cmd(session, repoids, convert_to_unicode=True,
                      verbose_warning=True)
    print("whereis info populated")


def populate_database(session):
    now = datetime.now()
    print("Creating git-annex find output")
    find_output_filename = make_find_output()
    print("Finished creating git-annex find output")
    print("Time taken for git-annex find: %s" % (datetime.now() - now))
    kl = make_keyid_lookup_dict(session)
    if not len(kl):
        initialize_annex_keys(session, find_output_filename)
        kl = make_keyid_lookup_dict(session)
    if not len(kl):
        raise RuntimeError("No key database")
    add_files(session, kl, find_output_filename)
    session.commit()
    os.remove(find_output_filename)
    # populate_whereis(session)


################################
# JUNK
################################
junk = """
def _various_queries():
    mq = s.query(AnnexKey, AnnexFile)
    fq = mq.filter(AnnexKey.id == AnnexFile.key_id)
    ###oq = fq.order_by(AnnexFile.name)
    oq = fq.order_by(AnnexKey.id)
    acf = aliased(func.count(AnnexFile.key_id))
    cf = func.count(AnnexFile.key_id).label('key_count')

    cq = s.query(AnnexFile.key_id, cf).group_by(AnnexFile.key_id).subquery()
    #q = s.query(AnnexFile, cq).filter(AnnexFile.key_id == cq.key_id)
    #q = s.query(AnnexFile, cq).filter(cq.count > 3)
    dq = s.query(cq).filter(cq.c.key_count > 1)

    #q = make_dupe_count_query(s)
    sq = make_dupe_count_query(s).subquery()

    #q = s.query(sq, AnnexFile).filter(sq.c.key_id == AnnexFile.key_id)
         .order_by(AnnexFile.key_id)
    q = s.query(sq, AnnexKey).filter(
        sq.c.key_id == AnnexKey.id).order_by(AnnexKey.id)
"""
