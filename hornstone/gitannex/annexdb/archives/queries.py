from sqlalchemy import func
from sqlalchemy import or_, and_

from hornstone.gitannex.annexdb.schema import AnnexKey, AnnexFile
from hornstone.gitannex.annexdb.schema import ArchiveFile, ArchiveEntry
from hornstone.gitannex.annexdb.schema import ArchiveEntryKey


dt_isoformat = '%Y-%m-%dT%H:%M:%S'


def archive_filename_filter(query, oclass, attr, rarfiles=False):
    likezip = getattr(oclass, attr).like('%.zip')
    likerar = getattr(oclass, attr).like('%.rar')
    if rarfiles:
        return query.filter(or_(likezip, likerar))
    return query.filter(likezip)


def archive_filename_query(session, oclass, attr, rarfiles=False):
    query = session.query(oclass)
    return archive_filename_filter(query, oclass, attr, rarfiles=rarfiles)


def get_annexed_archives_query(session, rarfiles=False):
    return archive_filename_query(session, AnnexFile,
                                  'name', rarfiles=rarfiles)


def get_entry_archives_query(session, rarfiles=False):
    return archive_filename_query(session, ArchiveEntry,
                                  'filename', rarfiles=rarfiles)


def get_archive_files_new(query, rarfiles=False):
    q = archive_filename_filter(query, AnnexFile, 'name',
                                rarfiles=rarfiles)
    return q.all()


def get_archive_files(query, rarfiles=False):
    files = list()
    for afile in query:
        name = afile.name.lower()
        # print "Name is %s" % name
        if name.endswith('.zip'):
            files.append(afile)
        elif rarfiles and name.endswith('.rar'):
            files.append(afile)
        else:
            continue
    return files


def annexed_archives_query(session):
    annex_query = session.query(AnnexFile)
    archives_subquery = session.query(ArchiveFile.id).subquery()
    in_archives_clause = AnnexFile.id.in_(archives_subquery)
    return annex_query.filter(in_archives_clause)


def common_key_query(session):
    q = session.query(AnnexKey, ArchiveEntryKey)
    q = q.filter(AnnexKey.name == ArchiveEntryKey.name)
    return q


def count_archive_annex_key_func():
    return func.count(AnnexFile.key_id).label('key_count')

# this returns a tuple of two integers
# (key_id, count(key_id))


def make_dupe_archive_entry_count_query(session):
    cf = count_archive_annex_key_func()
    cq = session.query(ArchiveEntry.key_id, cf).group_by(ArchiveEntry.key_id)
    cq = cq.subquery()
    return session.query(cq).filter(cq.c.key_count > 1)


################################
# Zips inside of zips
################################


def get_archive_entry_archive_files_query(session,
                                          toplevel=True, rarfiles=False):
    likezip = ArchiveEntry.filename.like('%.zip')
    likerar = ArchiveEntry.filename.like('%.rar')
    if rarfiles:
        filter = or_(likezip, likerar)
    else:
        filter = likezip
    if toplevel:
        filter = and_(filter, ArchiveEntry.entry_id is None)
    return session.query(ArchiveEntry).filter(filter)


def get_toplevel_annex_file(session, entry):
    return entry.archive.file
