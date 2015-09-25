import os
import json
from datetime import datetime
import zipfile
import tempfile

from sqlalchemy import func
from sqlalchemy import distinct
from sqlalchemy import or_, and_
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
        filter = and_(filter, ArchiveEntry.entry_id == None)
    return session.query(ArchiveEntry).filter(filter)

def get_toplevel_annex_file(session, entry):
    return entry.archive.file

def make_archive_entry_zipfile(session, entry, annexpath=None):
    filename = entry.archive.file.name
    if annexpath is not None:
        filename = os.path.join(annexpath, filename)
    if not filename.endswith('.zip'):
        raise RuntimeError, "Need only zipfiles now"
    with zipfile.ZipFile(filename, 'r') as zfile:
        info = zfile.getinfo(entry.filename)
        prefix = 'gitannex-archive-entry-archive-'
        ignore, tzfilename = tempfile.mkstemp(prefix=prefix, suffix='.zip')
        with file(tzfilename, 'w') as outfile, zfile.open(info) as infile:
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
    entry_id = archive_entry.id
    for entry in tzentries:
        pass
    
    
def insert_archive_entry_archive_files(session, sha256sum=True,
                                       toplevel=True, rarfiles=False):
    entries = get_archive_entry_archive_files_query(session)
    for entry in entries:
        tzfilename = make_archive_entry_zipfile(session, entry)
        tzentries = parse_archive_file(tzfilename, sha256sum=True)
        os.remove(tzfilename)
        
    
