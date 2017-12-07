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

EXAMPLE_ARCHIVE_DATA = dict(
    # don't keep database id
    # don't keep database key_id
    # this id should be filename -> <id>.json
    id='SHA256-size-checksum',
    archive_type='zip',
    bytesize=12311,
    entries=[],
    # key and id are equivalent
    key='SHA256-size-checksum',
    # these are in annex file already
    hashdirlower='',
    hashdirmixed='',
    humansize='',
    keyname='checksum',
    mtime=None,
    name='filename.zip',
    unicode_decode_error=False)


def _export_archive_file_dbobject(archivefile):
    entries = [e.serialize() for e in archivefile.entries]
    data = dict(entries=entries,
                archive_type=archivefile.archive_type)
    return data


def export_archive_manifest(session, fileid=None, name=None):
    if fileid is None and name is None:
        raise RuntimeError("need either fileid or name")
    if fileid is not None:
        afile = session.query(ArchiveFile).get(fileid)
    elif name is not None:
        q = session.query(ArchiveFile, AnnexFile).filter(
            AnnexFile.name == name)
        afile = q.one()
    if afile is not None:
        return _export_archive_file_dbobject(afile)


def export_annexed_archive_data(session, annexed_file):
    data = annexed_file.serialize()
    if 'key' in data:
        raise RuntimeError("bad data %s" % data)
    data['key'] = annexed_file.key.name
    arfile = session.query(ArchiveFile).get(annexed_file.id)
    if arfile is not None:
        data.update(_export_archive_file_dbobject(arfile))
    return data


def export_archive_to_file(session, annexed_file, directory):
    data = export_annexed_archive_data(session, annexed_file)
    name = '%s.json' % data['key']
    filename = os.path.join(directory, name)
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


def annexed_archives_query(session):
    annex_query = session.query(AnnexFile)
    archives_subquery = session.query(ArchiveFile.id).subquery()
    in_archives_clause = AnnexFile.id.in_(archives_subquery)
    return annex_query.filter(in_archives_clause)


def export_all_archives(session, zipfilename, fail_on_dupe=False):
    annexed_archives = annexed_archives_query(session)
    keys = list()
    with zipfile.ZipFile(zipfilename, 'w') as zfile:
        for afile in annexed_archives:
            print("Exporting", afile.name)
            data = export_annexed_archive_data(session, afile)
            key = data['key']
            if key not in keys:
                keys.append(key)
            else:
                archive = afile.name
                if fail_on_dupe:
                    tmpl = "Already have key %s for annexed archive %s"
                    raise RuntimeError(tmpl % (key, archive))
                else:
                    print("Skipping duplicate annexed archive %s" % archive)
                    continue
            arcname = '%s.json' % key
            fbytes = json.dumps(data)
            zfile.writestr(arcname, fbytes, zipfile.ZIP_DEFLATED)
            #zfile.writestr(arcname, fbytes, zipfile.ZIP_STORED)
    return annexed_archives
