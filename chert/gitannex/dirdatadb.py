from datetime import datetime, date
import time

from sqlalchemy import Sequence, Column, ForeignKey

# column types
from sqlalchemy import Integer, String, Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean, Date, LargeBinary
from sqlalchemy import PickleType
from sqlalchemy import Enum
from sqlalchemy import DateTime

from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base


from chert.alchemy import SerialBase

Base = declarative_base()
    

####################################
## Data Types                     ##
####################################

HubbyFileType = Enum('agenda', 'minutes', 'attachment',
                name='hubbyfile_type_enum')

GitAnnexBackendType = Enum('SHA256', 'SHA256E',
                           name='gitannex_backend_type_enum')

ArchiveType = Enum('zip', 'rar', '7z',
                   name='archive_file_type_enum')

####################################
## Tables                         ##
####################################
#

class AnnexKey(Base, SerialBase):
    __tablename__ = "annex_keys"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), unique=True)

class AnnexFile(Base, SerialBase):
    __tablename__ = "annex_files"
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, unique=True)
    key_id = Column(Integer, ForeignKey('annex_keys.id'))
    backend = Column(GitAnnexBackendType)
    bytesize = Column(Integer)
    humansize = Column(Unicode(50))
    keyname = Column(Unicode(100))
    hashdirlower = Column(Unicode(10))
    hashdirmixed = Column(Unicode(10))
    # null mtime is "unknown"
    mtime = Column(DateTime)


class ArchiveFile(Base, SerialBase):
    __tablename__ = "archive_files"
    id = Column(Integer, ForeignKey('annex_files.id'), primary_key=True)
    archive_type = Column(ArchiveType)

class ArchiveEntry(Base, SerialBase):
    __tablename__ = "archive_entries"
    id = Column(Integer, primary_key=True)
    archive_id = Column(Integer, ForeignKey('archive_files.id'))
    entry_id = Column(Integer)
    archive_type = Column(ArchiveType)
    bytesize = Column(Integer)
    sha256sum = Column(Unicode(100))

    # both rar and zip
    crc = Column(Integer)
    comment = Column(Unicode(200))
    compress_size = Column(Integer)
    date_time = Column(DateTime)
    filename = Column(UnicodeText)
    file_size = Column(Integer)
    volume = Column(Integer)

    # in both rar and zip, but not compatible
    compress_type = Column(Integer)
    extract_version = Column(Integer)
    header_offset = Column(Integer)
    orig_filename = Column(UnicodeText)
    
    # in zip files
    create_system = Column(Integer)
    create_version = Column(Integer)
    external_attr = Column(Integer)
    extra = Column(Unicode(200))
    flag_bits = Column(Integer)
    internal_attr = Column(Integer)
    reserved = Column(Integer)
    
    # in rar files
    add_size = Column(Integer)
    arctime = Column(DateTime)
    atime = Column(DateTime)
    ctime = Column(DateTime)
    file_offset = Column(Integer)
    flags = Column(Integer)
    header_base = Column(Integer)
    header_crc = Column(Integer)
    header_data = Column(UnicodeText)
    header_size = Column(Integer)
    host_os = Column(Integer)
    mode = Column(Integer)
    mtime = Column(DateTime)
    name_size = Column(Integer)
    salt = Column(UnicodeText)
    type = Column(Integer)
    volume_file = Column(UnicodeText)
    

####################################
## Relationships                  ##
####################################

AnnexFile.key = relationship(AnnexKey, backref='files')
ArchiveFile.file = relationship(AnnexFile)
ArchiveFile.entries = relationship(ArchiveEntry, backref='archive')
