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
from sqlalchemy import BigInteger

from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base


from chert.alchemy import SerialBase

Base = declarative_base()
    

####################################
## Data Types                     ##
####################################

#GitAnnexBackendType = Enum('SHA256', 'SHA256E',
#                           name='gitannex_backend_type_enum')


####################################
## Tables                         ##
####################################
#



vccol = Unicode(200)

class GitHubUser(Base, SerialBase):
    __tablename__ = 'ghub_users'
    id = Column(BigInteger, primary_key=True)
    login = Column(vccol, unique=True)
    avatar_url = Column(vccol)
    gravatar_id = Column(vccol)
    url = Column(vccol)
    html_url = Column(vccol)
    followers_url = Column(vccol)
    following_url = Column(vccol)
    gists_url = Column(vccol)
    starred_url = Column(vccol)
    subscriptions_url = Column(vccol)
    organizations_url = Column(vccol)
    repos_url = Column(vccol)
    events_url = Column(vccol)
    received_events_url = Column(vccol)
    type = Column(vccol)
    site_admin = Column(Boolean)
    name = Column(vccol)
    company = Column(vccol)
    blog = Column(vccol)
    location = Column(vccol)
    email = Column(vccol)
    hireable = Column(Boolean)
    bio = Column(vccol)
    public_repos = Column(Integer)
    public_gists = Column(Integer)
    followers = Column(Integer)
    following = Column(Integer)
    created_at_gh = Column(DateTime)
    updated_at_gh = Column(DateTime)
    pickle = Column(PickleType)
    created = Column(DateTime)
    updated = Column(DateTime)

    
class GitHubRepo(Base, SerialBase):
    __tablename__ = 'ghub_repos'
    id = Column(BigInteger, primary_key=True)
    owner_id = Column(BigInteger, ForeignKey('ghub_users.id')
    name = Column(vccol)
    full_name = Column(vccol)
    description = Column(UnicodeText)
    private = Column(Boolean)
    fork = Column(Boolean)
    default_branch = Column(vccol)
    homepage = Column(vccol)
    url = Column(vccol)
    html_url = Column(vccol)
    has_issues = Column(Boolean)
    has_wiki = Column(Boolean)
    has_pages = Column(Boolean)
    has_downloads = Column(Boolean)
    size = Column(Integer)
    forks_count = Column(Integer)
    stargazers_count = Column(Integer)
    open_issues_count = Column(Integer)
    pushed_at_gh = Column(DateTime)
    created_at_gh = Column(DateTime)
    updated_at_gh = Column(DateTime)
    pickle = Column(PickleType)
    created = Column(DateTime)
    updated = Column(DateTime)
    
    
    
####################################
## Relationships                  ##
####################################

#AnnexFile.key = relationship(AnnexKey, backref='files')
#ArchiveFile.file = relationship(AnnexFile)
#ArchiveFile.entries = relationship(ArchiveEntry, backref='archive')
#ArchiveEntry.key = relationship(ArchiveEntryKey, backref='entries')
#RepoFile.file = relationship(AnnexFile, backref='repositories')
