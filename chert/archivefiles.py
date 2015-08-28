#!/usr/bin/env python
from datetime import datetime
import zipfile

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

def parse_archive_file(filename, sha256sum=False):
    archive_type = get_archive_type(filename)
    fileclass = ARCHIVE_FILECLASS[archive_type]
    entries = list()
    with fileclass(filename, 'r') as afile:
        for ainfo in afile.infolist():
            if archive_type == 'rar' and ainfo.isdir():
                print "Skipping directory entry %s" % ainfo.filename
                continue
            parsed = parse_archive_info(ainfo, archive_type)
            parsed['bytesize'] = ainfo.file_size
            if sha256sum:
                fileobj = afile.open(ainfo)
                sha256sum = get_sha256sum(fileobj)
                parsed['sha256sum'] = sha256sum
            entries.append(parsed)
    return entries


