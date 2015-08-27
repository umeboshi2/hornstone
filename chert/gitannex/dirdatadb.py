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



####################################
## Relationships                  ##
####################################

AnnexFile.key = relationship(AnnexKey)
