import uuid
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import UUIDType

from ..alchemy import TimeStampMixin


class BaseUUIDMixin(TimeStampMixin):
    @declared_attr
    def id(self):
        return sa.Column(UUIDType, primary_key=True,
                         default=uuid.uuid4)


class BaseIdMixin(TimeStampMixin):
    @declared_attr
    def id(self):
        return sa.Column(sa.Integer, primary_key=True, autoincrement=True)


class UserOwnedMixin(TimeStampMixin):
    @declared_attr
    def user_id(self):
        return sa.Column(UUIDType, sa.ForeignKey('users.id'))

# FIXME these name mixins are probably not useful


class BaseShortNameIdMixin(BaseIdMixin):
    @declared_attr
    def name(self):
        return sa.Column(sa.Unicode(50), unique=True)


class BaseShortNameUUIDMixin(BaseUUIDMixin):
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


class BaseNameUUIDMixin(BaseUUIDMixin):
    @declared_attr
    def name(self):
        return sa.Column(sa.Unicode, unique=True)
