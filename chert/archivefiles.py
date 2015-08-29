#!/usr/bin/env python
import os
from datetime import datetime
import zipfile
import tempfile
import subprocess

#from useless.base.path import path
from unipath.path import Path as path
from unipath import FILES, DIRS, LINKS

import rarfile
rarfile.UNRAR_TOOL = 'rar'


from chert.base import get_sha256sum

# date_time and CRC handled separately
COMPATIBLE_ARCHIVE_INFO_ATTRIBUTES = ['comment', 'compress_size',
                                      'filename',
                                      'file_size', 'volume']
COMMON_ARCHIVE_INFO_ATTRIBUTES = ['compress_type', 'extract_version',
                                  'header_offset', 'orig_filename']
ONLY_ZIP_INFO_ATTRIBUTES = ['create_system', 'create_version',
                            'external_attr', 'extra', 'flag_bits',
                            'internal_attr', 'reserved']
ONLY_RAR_INFO_ATTRIBUTES = ['add_size', 'arctime', 'atime', 'ctime',
                            'file_offset', 'flags', 'header_base',
                            'header_crc', 'header_data', 'header_size',
                            'host_os', 'mode', 'mtime',
                            'name_size', 'salt', 'type',
                            'volume_file']

_COMMON = COMPATIBLE_ARCHIVE_INFO_ATTRIBUTES + COMMON_ARCHIVE_INFO_ATTRIBUTES
ZIP_INFO_ATTRIBUTES = _COMMON + ONLY_ZIP_INFO_ATTRIBUTES
RAR_INFO_ATTRIBUTES = _COMMON + ONLY_RAR_INFO_ATTRIBUTES
ARCHIVE_ATTRIBUTES = dict(zip=ZIP_INFO_ATTRIBUTES, rar=RAR_INFO_ATTRIBUTES)
ARCHIVE_FILECLASS = dict(zip=zipfile.ZipFile, rar=rarfile.RarFile)


def parse_archive_info(info, archive_type, sha256sum=False):
    #print "Parsing", info.filename
    data = dict()
    for att in ARCHIVE_ATTRIBUTES[archive_type]:
        value = getattr(info, att)
        if type(value) is str:
            value = unicode(value, errors='replace')
        data[att] = value
    # handle CRC for file
    data['crc'] = info.CRC
    data['date_time'] = datetime(*info.date_time)
    return data

def get_archive_type(filename):
    lname = filename.lower()
    if lname.endswith('.zip'):
        archive_type = 'zip'
    elif lname.endswith('.rar'):
        archive_type = 'rar'
    else:
        raise RuntimeError, "unable to handle archive %s" % filename    
    return archive_type


def scan_directory_tree(dirname):
    dirname = path(dirname)
    entries = list()
    for fname in dirname.walk(filter=FILES):
        filename = unicode(dirname.rel_path_to(fname), errors='replace')
        ifile = file(fname)
        ifile.seek(0, 2)
        file_size = ifile.tell()
        ifile.seek(0)
        sha256sum = get_sha256sum(ifile)
        entry = dict(filename=filename,
                     sha256sum=sha256sum,
                     file_size=file_size,
                     bytesize=file_size)
        entries.append(entry)
    return entries

        
def parse_rar_archive(filename, sha256sum=False):
    tmpdir = tempfile.mkdtemp(prefix='extracted-rar-')
    cmd = ['rar', 'x', filename, tmpdir]
    subprocess.check_call(cmd)
    here = path.cwd()
    os.chdir(tmpdir)
    td = path(tmpdir)
    entries = scan_directory_tree(td)
    cmd = ['rm', '-fr', tmpdir]
    subprocess.check_call(cmd)
    os.chdir(here)
    return entries

def parse_zip_archive(filename, sha256sum=False):
    entries = list()
    with zipfile.ZipFile(filename, 'r') as afile:
        for ainfo in afile.infolist():
            parsed = parse_archive_info(ainfo, 'zip')
            parsed['bytesize'] = ainfo.file_size
            if sha256sum:
                fileobj = afile.open(ainfo)
                sha256sum = get_sha256sum(fileobj)
                parsed['sha256sum'] = sha256sum
            entries.append(parsed)
    return entries

archive_parser = dict(zip=parse_zip_archive, rar=parse_rar_archive)
            
def parse_archive_file(filename, sha256sum=False):
    archive_type = get_archive_type(filename)
    return archive_parser[archive_type](filename, sha256sum=sha256sum)

