from sqlalchemy import Column, ForeignKey

# column types
from sqlalchemy import (
    Integer,
    Unicode,
    UnicodeText,
    Enum,
    )
from sqlalchemy.orm import relationship

from hornstone.alchemy import Base, SerialBase

####################################
# Data Types                     ###
####################################

HubbyFileType = Enum('agenda', 'minutes', 'attachment',
                     name='hubbyfile_type_enum')

####################################
# Tables                         ###
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
# Relationships                  ###
####################################

ScummVMGame.company = relationship(ScummVMCompany)
