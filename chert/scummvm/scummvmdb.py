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

####################################
## Tables                         ##
####################################


class ScummVMCompany(Base, SerialBase):
    __tablename__ = 'scummvm_companies'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), unique=True)


class ScummVMGame(Base, SerialBase):
    __tablename__ = 'scummvm_games'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(300))
    company_id = Column(Integer, ForeignKey('scummvm_companies.id'))
    support_level = Column(Unicode(100))
    notes = Column(UnicodeText)


####################################
## Relationships                  ##
####################################

ScummVMGame.company = relationship(ScummVMCompany)
