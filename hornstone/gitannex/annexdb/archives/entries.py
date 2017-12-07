import os
import zipfile
import tempfile

from sqlalchemy import or_, and_

from hornstone.archivefiles import parse_archive_file


from hornstone.gitannex.annexdb.schema import ArchiveEntry


dt_isoformat = '%Y-%m-%dT%H:%M:%S'


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


def make_archive_entry_zipfile(session, entry, annexpath=None):
    filename = entry.archive.file.name
    if annexpath is not None:
        filename = os.path.join(annexpath, filename)
    if not filename.endswith('.zip'):
        raise RuntimeError("Need only zipfiles now")
    with zipfile.ZipFile(filename, 'r') as zfile:
        info = zfile.getinfo(entry.filename)
        prefix = 'gitannex-archive-entry-archive-'
        ignore, tzfilename = tempfile.mkstemp(prefix=prefix, suffix='.zip')
        with open(tzfilename, 'w') as outfile, zfile.open(info) as infile:
            while True:
                block = infile.read(4096)
                if not block:
                    break
                outfile.write(block)
    return tzfilename


def insert_archive_entry_archive_entry(session, archive_entry, entry):
    pass


def insert_archive_entry_archive(session, archive_entry):
    tzfilename = make_archive_entry_zipfile(session, archive_entry)
    tzentries = parse_archive_file(tzfilename, sha256sum=True)
    os.remove(tzfilename)
    for entry in tzentries:
        pass


def insert_archive_entry_archive_files(session, sha256sum=True,
                                       toplevel=True, rarfiles=False):
    entries = get_archive_entry_archive_files_query(session)
    for entry in entries:
        tzfilename = make_archive_entry_zipfile(session, entry)
        os.remove(tzfilename)
