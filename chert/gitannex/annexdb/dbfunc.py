import os
import json
from datetime import datetime
import zipfile

from sqlalchemy import func
from sqlalchemy import distinct
from sqlalchemy import or_
from sqlalchemy import desc

from sqlalchemy.orm.exc import NoResultFound

from chert.base import remove_trailing_slash

from chert.archivefiles import parse_archive_file
from chert.archivefiles import get_archive_type

from chert.gitannex import make_old_default_key, make_default_key

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
