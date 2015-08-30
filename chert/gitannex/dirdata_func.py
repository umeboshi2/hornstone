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

from chert.gitannex.dirdatadb import AnnexKey, AnnexFile
from chert.gitannex.dirdatadb import ArchiveFile, ArchiveEntry
from chert.gitannex.dirdatadb import ArchiveEntryKey


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

                     
####################################
# archive files
####################################
def get_archive_files(query, rarfiles=False):
    files = list()
    for afile in query:
        name = afile.name.lower()
        #print "Name is %s" % name
        if name.endswith('.zip'):
            files.append(afile)
        elif rarfiles and  name.endswith('.rar'):
            files.append(afile)
        else:
            continue
    return files
    
def populate_db_archive_entry(dbobj, parsed_entry, archive_type):
    for key in ['ctime', 'mtime', 'atime']:
        if key in parsed_entry and parsed_entry[key] is not None:
            value = parsed_entry[key]
            if type(value) is tuple:
                parsed_entry[key] = datetime(*(int(t) for t in parsed_entry[key]))
            elif type(value) is str:
                parsed_entry[key] = datetime.strptime(value, dt_isoformat)
    for key in parsed_entry:
        value = parsed_entry[key]
        setattr(dbobj, key, value)
    dbobj.archive_type = archive_type

def make_key_from_archive_entry(entry, oldkey=True):
    size = entry['bytesize']
    checksum = entry['sha256sum']
    if oldkey:
        return make_old_default_key(size, checksum)
    ext = entry['filename'].split('.')[-1]
    return make_default_key(size, checksum, ext)

def create_archive_entry_key(session, key):
    dbkey = ArchiveEntryKey()
    dbkey.name = key
    session.add(dbkey)
    return session.merge(dbkey)

def get_archive_entry_key(session, entry, oldkey=True):
    key = make_key_from_archive_entry(entry, oldkey=oldkey)
    try:
        dbkey = session.query(ArchiveEntryKey).filter_by(name=key).one()
    except NoResultFound:
        dbkey = create_archive_entry_key(session, key)
    return dbkey

        
def insert_archive_file(session, afile, sha256sum=True,
                        archive_data=None):
    archived = session.query(ArchiveFile).get(afile.id)
    if archived is None:
        print "need to archive", afile.name
        if archive_data is None:
            entries = parse_archive_file(afile.name, sha256sum=sha256sum)
        else:
            entries = archive_data['entries']
    else:
        print "Archive should be available"
        return
    if archive_data is None:
        archive_type = get_archive_type(afile.name)
    else:
        archive_type = archive_data['archive_type']
    af = ArchiveFile()
    af.id = afile.id
    af.archive_type = archive_type
    session.add(af)
    for entry in entries:
        dbkey = get_archive_entry_key(session, entry, oldkey=True)
        #import pdb ; pdb.set_trace()
        dbobj = ArchiveEntry()
        populate_db_archive_entry(dbobj, entry, archive_type)
        dbobj.archive_id = afile.id
        dbobj.key_id = dbkey.id
        if archive_data is not None:
            dbobj.date_time = datetime.strptime(dbobj.date_time, dt_isoformat)
            for att in ['ctime', 'mtime', 'atime']:
                value = getattr(dbobj, att)
                if value  is not None: 
                    dt = datetime.strptime(value, dt_isoformat)
                    setattr(dbobj, att, dt)
        session.add(dbobj)
    session.commit()
    print "Successful commit of %s with %d entries" % (afile.name, len(entries))

def _export_archive_file_dbobject(archivefile):
    entries = [e.serialize() for e in archivefile.entries]
    data = dict(entries=entries, 
                archive_type=archivefile.archive_type)
    return data



    
def export_archive_manifest(session, fileid=None, name=None):
    if fileid is None and name is None:
        raise RuntimeError, "need either fileid or name"
    if fileid is not None:
        afile = session.query(ArchiveFile).get(fileid)
    elif name is not None:
        q = session.query(ArchiveFile, AnnexFile).filter(AnnexFile.name == name)
        afile = q.one()
    if afile is not None:
        return _export_archive_file_dbobject(afile)

    
def export_annexed_archive_data(session, annexed_file):
    data = annexed_file.serialize()
    if 'key' in data:
        raise RuntimeError, "bad data %s" % data
    data['key'] = annexed_file.key.name
    arfile = session.query(ArchiveFile).get(annexed_file.id)
    if arfile is not None:
        data.update(_export_archive_file_dbobject(arfile))
    return data

def export_archive_to_file(session, annexed_file, directory):
    data = export_annexed_archive_data(session, annexed_file)
    name = '%s.json' % data['key']
    filename = os.path.join(directory, name)
    with file(filename, 'w') as outfile:
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
            print "Exporting", afile.name
            data = export_annexed_archive_data(session, afile)
            key = data['key']
            if key not in keys:
                keys.append(key)
            else:
                archive = afile.name
                if fail_on_dupe:
                    tmpl = "Already have key %s for annexed archive %s"
                    raise RuntimeError, tmpl % (key, archive)
                else:
                    print "Skipping duplicate annexed archive %s" % archive
                    continue
            arcname = '%s.json' % key
            fbytes = json.dumps(data)
            zfile.writestr(arcname, fbytes, zipfile.ZIP_DEFLATED)
            #zfile.writestr(arcname, fbytes, zipfile.ZIP_STORED)
    return annexed_archives


def _get_annex_key(session, key, fail_on_duplicate_archives=False):
    try:
        annex_key = session.query(AnnexKey).filter_by(name=key).one()
    except NoResultFound:
        raise RuntimeError, "No annexed file for %s" % key
    have_duplicates = len(annex_key.files) > 1
    if have_duplicates:
        dfiles = ', '.join((x.name for x in annex_key.files))
        print "Duplicate archives in annex: %s" % dfiles
    if fail_on_duplicate_archives and have_duplicates:
        raise RuntimeError, "Duplicate archives in annex: %s" % dfiles
    return annex_key

def import_annexed_archive_data(session, archive_data,
                                fail_on_duplicate_archives=False):
    data = archive_data
    archive_type = data['archive_type']
    key = data['key']
    annex_key = _get_annex_key(
        session, key,
        fail_on_duplicate_archives=fail_on_duplicate_archives)
    annex_file = annex_key.files[0]
    insert_archive_file(session, annex_file,
                        archive_data=data)
    

    
    

def import_annexed_archives(session, zipfilename):
    with zipfile.ZipFile(zipfilename, 'r') as zfile:
        for ainfo in zfile.infolist():
            data = json.load(zfile.open(ainfo))
            import_annexed_archive_data(session, data)
            
            

    

# don't do this!!!!        
def export_all_archives_orig(session, annex_file_query, directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)
    if not os.path.isdir(directory):
        raise RuntimeError, "%s not created." % directory
    archive_files = get_archive_files(annex_file_query)
    for annexed_file in archive_files:
        export_archive_to_file(session, annexed_file, directory)
        

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



def delete_archive_dbobjects(session):
    for obj in ArchiveEntry, ArchiveEntryKey, ArchiveFile:
        session.query(obj).delete()
    session.commit()
    


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
