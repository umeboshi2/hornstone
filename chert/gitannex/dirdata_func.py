from sqlalchemy import func
from sqlalchemy import distinct

from chert.gitannex.dirdatadb import AnnexKey, AnnexFile

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


# this will return paths that are not
# necessarily under the parent, but one
# of the paths in the set of duplicates
# will be under the parent.
def dupekeys_under_parent(session, parent_directory):
    while parent_directory.endswith('/'):
        parent_directory = parent_directory[:-1]
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
