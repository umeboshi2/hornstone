from configparser import ConfigParser
from io import StringIO

import sqlalchemy as sa
from sqlalchemy import Column
from sqlalchemy import Integer, Boolean
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey, PickleType
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ..alchemy import TimeStampMixin

class BaseIdMixin(TimeStampMixin):
    @declared_attr
    def id(self):
        return sa.Column(sa.Integer, primary_key=True, autoincrement=True)

class UserOwnedMixin(TimeStampMixin):
    @declared_attr
    def user_id(self):
        return sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    
# FIXME these name mixins are probably not useful

    
class BaseShortNameIdMixin(BaseIdMixin):
    @declared_attr
    def name(self):
        return sa.Column(sa.Unicode(50), unique=True)

class BaseLongNameIdMixin(BaseIdMixin):
    @declared_attr
    def name(self):
        return sa.Column(sa.Unicode(255), unique=True)

class BaseNameIdMixin(BaseIdMixin):
    @declared_attr
    def name(self):
        return sa.Column(sa.Unicode, unique=True)


