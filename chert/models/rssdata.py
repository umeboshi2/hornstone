from configparser import ConfigParser
from io import StringIO

import sqlalchemy as sa
from sqlalchemy import Column
from sqlalchemy import Integer, Boolean
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey, PickleType, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from chert.alchemy import TimeStampMixin


class FeedMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'rssfeeds'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def name(self):
        return Column(Unicode(100), unique=True)

    @declared_attr
    def url(self):
        return Column(Unicode(100), unique=True)


class FeedDataMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'rssdata'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def feed_id(self):
        return Column(Integer, ForeignKey('rssfeeds.id'))

    @declared_attr
    def content(self):
        return Column(PickleType)

    @declared_attr
    def retrieved(self):
        return Column(DateTime)

    @declared_attr
    def feed(self):
        return relationship('Feed')
