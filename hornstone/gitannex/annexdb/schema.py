from sqlalchemy import Column, ForeignKey

# column types
from sqlalchemy import Integer, Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean
from sqlalchemy import Enum
from sqlalchemy import DateTime
from sqlalchemy import BigInteger

from sqlalchemy.orm import relationship

from hornstone.alchemy import SerialBase


####################################
#  Data Types                     ##
####################################

GitAnnexBackendType = Enum('SHA256', 'SHA256E',
                           name='gitannex_backend_type_enum')

ArchiveType = Enum('zip', 'rar', '7z',
                   name='ga_archive_file_type_enum')

AnnexRepositoryTrustType = Enum('trusted', 'semitrusted', 'untrusted', 'dead',
                                name='gitannex_repository_trust_type')

####################################
#  Tables                         ##
####################################
#


class AnnexRepository(SerialBase):
    __tablename__ = 'ga_annex_repositories'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200))
    uuid = Column(Unicode(40), unique=True)
    trust = Column(AnnexRepositoryTrustType, default='semitrusted')


class AnnexKey(SerialBase):
    __tablename__ = "ga_annex_keys"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), unique=True)


class AnnexFile(SerialBase):
    __tablename__ = "ga_annex_files"
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, unique=True)
    key_id = Column(Integer, ForeignKey('ga_annex_keys.id'))
    backend = Column(GitAnnexBackendType)
    bytesize = Column(BigInteger)
    humansize = Column(Unicode(50))
    keyname = Column(Unicode(100))
    hashdirlower = Column(Unicode(10))
    hashdirmixed = Column(Unicode(10))
    # null mtime is "unknown"
    mtime = Column(DateTime)
    unicode_decode_error = Column(Boolean)


class RepoFile(SerialBase):
    __tablename__ = "ga_annex_repo_files"
    file_id = Column(Integer, ForeignKey('ga_annex_files.id'),
                     primary_key=True)
    repo_id = Column(Integer, ForeignKey('ga_annex_repositories.id'),
                     primary_key=True)


class ArchiveFile(SerialBase):
    __tablename__ = "ga_archive_files"
    id = Column(Integer, ForeignKey('ga_annex_files.id'), primary_key=True)
    archive_type = Column(ArchiveType)


class ArchiveEntryKey(SerialBase):
    __tablename__ = "ga_archive_entry_keys"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), unique=True)


class ArchiveEntry(SerialBase):
    __tablename__ = "ga_archive_entries"
    id = Column(Integer, primary_key=True)
    archive_id = Column(Integer, ForeignKey('ga_archive_files.id'))
    entry_id = Column(Integer)
    key_id = Column(Integer, ForeignKey('ga_archive_entry_keys.id'))
    archive_type = Column(ArchiveType)
    bytesize = Column(BigInteger)
    sha256sum = Column(Unicode(100))
    unicode_decode_error = Column(Boolean)

    # both rar and zip
    crc = Column(BigInteger)
    comment = Column(Unicode(200))
    compress_size = Column(BigInteger)
    date_time = Column(DateTime)
    filename = Column(UnicodeText)
    file_size = Column(BigInteger)
    volume = Column(Integer)

    # in both rar and zip, but not compatible
    compress_type = Column(Integer)
    extract_version = Column(Integer)
    header_offset = Column(BigInteger)
    orig_filename = Column(UnicodeText)

    # in zip files
    create_system = Column(Integer)
    create_version = Column(Integer)
    external_attr = Column(BigInteger)
    extra = Column(Unicode(200))
    flag_bits = Column(Integer)
    internal_attr = Column(Integer)
    reserved = Column(Integer)

    # in rar files
    add_size = Column(BigInteger)
    arctime = Column(DateTime)
    atime = Column(DateTime)
    ctime = Column(DateTime)
    file_offset = Column(BigInteger)
    flags = Column(Integer)
    header_base = Column(Integer)
    header_crc = Column(Integer)
    header_data = Column(UnicodeText)
    header_size = Column(Integer)
    host_os = Column(Integer)
    mode = Column(Integer)
    mtime = Column(DateTime)
    name_size = Column(BigInteger)
    salt = Column(UnicodeText)
    type = Column(Integer)
    volume_file = Column(UnicodeText)


####################################
#  Relationships                  ##
####################################

AnnexFile.key = relationship(AnnexKey, backref='files')
ArchiveFile.file = relationship(AnnexFile)
ArchiveFile.entries = relationship(ArchiveEntry, backref='archive')
ArchiveEntry.key = relationship(ArchiveEntryKey, backref='entries')
RepoFile.file = relationship(AnnexFile, backref='repositories')
