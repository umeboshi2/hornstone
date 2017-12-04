from configparser import ConfigParser
from io import StringIO

import sqlalchemy as sa
from sqlalchemy import Column
from sqlalchemy import Integer, Boolean
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey, PickleType
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from chert.alchemy import TimeStampMixin

class CeleryTaskMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'celery_taskmeta'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, nullable=False)

    @declared_attr
    def task_id(self):
        return Column(Unicode(255))
    
    @declared_attr
    def status(self):
        return Column(Unicode(50))

    @declared_attr
    def result(self):
        return Column(PickleType)

    @declared_attr
    def date_done(self):
        return Column(DateTime)
    
    @declared_attr
    def traceback(self):
        return Column(UnicodeText)
