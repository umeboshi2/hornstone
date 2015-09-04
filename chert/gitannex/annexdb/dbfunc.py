import os
import json
from datetime import datetime
import zipfile
import tempfile

from sqlalchemy import func
from sqlalchemy import distinct
from sqlalchemy import or_
from sqlalchemy import desc

from sqlalchemy.orm.exc import NoResultFound

from chert.base import remove_trailing_slash

from chert.archivefiles import parse_archive_file
from chert.archivefiles import get_archive_type

from chert import gitannex

from chert.gitannex.annexdb.schema import AnnexKey, AnnexFile
from chert.gitannex.annexdb.schema import ArchiveFile, ArchiveEntry
from chert.gitannex.annexdb.schema import ArchiveEntryKey


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
    ddict = make_dupedict(dfq)
    sets_of_interest = dict()
    current_set = dict()
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
    psq = dfq.filter(AnnexFile.name.like('%s/%%' % parent_directory)).subquery()
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
    #import pdb ; pdb.set_trace()
    count = 0
    if output_to_file:
        outfile = file(output_filename, 'w')
    while proc.returncode is None:
        try:
            line = proc.stdout.next()
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


def initialize_annex_keys(session, find_output_filename):
    filename = find_output_filename
    keys = set()
    with file(filename) as infile:
        while True:
            try:
                line = infile.next()
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
    print "added %d keys" % len(keys)
    print datetime.now()
    session.commit()
    print "successful commit", datetime.now()




def _add_annexfile_attributes(keylookup, dbobj, data):
    key = data['key']
    try:
        dbobj.key_id = keylookup[key]
    except KeyError:
        raise KeyError, "Unknown key %s" % data

    dbobj.name = data['file']
    for att in ['backend', 'bytesize', 'humansize',
                'keyname', 'hashdirlower', 'hashdirmixed',
                'unicode_decode_error']:
        setattr(dbobj, att, data[att])
        if data['mtime'] != 'unknown':
            raise RuntimeError, "Parse time?"
        

def add_file_to_database(session, keylookup, filedata,
                         commit=False):
    dbobj = AnnexFile()
    _add_annexfile_attributes(keylookup, dbobj, filedata)
    session.add(dbobj)




def add_files(session, keylookup, find_output_filename):
    with file(find_output_filename) as infile:
        count = 0
        current = datetime.now()
        while True:
            try:
                line = infile.next()
                count += 1
            except StopIteration:
                break
            data = gitannex.parse_json_line(
                line,
                convert_to_unicode=True,
                verbose_warning=True)
            commit = False
            add_file_to_database(session, keylookup, data)
            if not count % 5000:
                commit = True
                print "Committing %d files" % count
                now = datetime.now()
                print "Diff", now - current
                current = now
                session.commit()
        print "%d files added." % count
        session.commit()
        print datetime.now()


def populate_database(session):
    now = datetime.now()
    print "Creating git-annex find output"
    find_output_filename = make_find_output()
    print "Finished creating git-annex find output"
    print "Time taken for git-annex find: %s" % (datetime.now() - now)
    kl = make_keyid_lookup_dict(session)
    if not len(kl):
        initialize_annex_keys(session, find_output_filename)
        kl = make_keyid_lookup_dict(session)
    if not len(kl):
        raise RuntimeError, "No key database"
    add_files(session, kl, find_output_filename)
    session.commit()
    os.remove(find_output_filename)
    
                     


################################
# JUNK
################################

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
    #q = s.query(sq, AnnexFile).filter(sq.c.key_id == AnnexFile.key_id).order_by(AnnexFile.key_id)
    q = s.query(sq, AnnexKey).filter(sq.c.key_id == AnnexKey.id).order_by(AnnexKey.id)
