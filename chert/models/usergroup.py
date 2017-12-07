from configparser import ConfigParser
from io import StringIO

from sqlalchemy import Column
from sqlalchemy import Integer, Boolean
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey, PickleType
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ..alchemy import TimeStampMixin
from .base import BaseIdMixin, BaseShortNameIdMixin


class UserMixin(BaseIdMixin):
    @declared_attr
    def __tablename__(self):
        return 'users'

    @declared_attr
    def username(self):
        return Column(Unicode(50), unique=True)

    @declared_attr
    def fullname(self):
        return Column(Unicode(150), unique=True)

    @declared_attr
    def email(self):
        return Column(Unicode(150), unique=True)

    @declared_attr
    def active(self):
        return Column(Boolean(name='user_active'), default=True)

    @declared_attr
    def password(self):
        return Column(Unicode(150))

    @declared_attr
    def settings(self):
        return Column(PickleType)

    @property
    def user_name(self):
        return super(TimeStampMixin, self).username

    def get_groups(self):
        return [g.name for g in self.groups]


class UserConfigMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'user_config'

    @declared_attr
    def id(self):
        return Column(Integer, ForeignKey('users.id'), primary_key=True)

    @declared_attr
    def text(self):
        return Column(UnicodeText)

    def get_config(self):
        c = ConfigParser()
        c.readfp(StringIO(self.text))
        return c

    def set_config(self, config):
        cfile = StringIO()
        config.write(cfile)
        cfile.seek(0)
        text = cfile.read()
        self.text = text


class GroupMixin(BaseShortNameIdMixin):
    @declared_attr
    def __tablename__(self):
        return 'groups'

    @declared_attr
    def description(self):
        return Column(UnicodeText)

    @declared_attr
    def users(self):
        return relationship('User', secondary='group_user',
                            backref='groups')


class UserGroupMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'group_user'

    @declared_attr
    def group_id(self):
        return Column(Integer,
                      ForeignKey('groups.id',
                                 onupdate='CASCADE',
                                 ondelete='CASCADE'),
                      primary_key=True)

    @declared_attr
    def user_id(self):
        return Column(Integer,
                      ForeignKey('users.id',
                                 onupdate='CASCADE',
                                 ondelete='CASCADE'),
                      primary_key=True)


# User.config = relationship(UserConfig, uselist=False, lazy='subquery')
