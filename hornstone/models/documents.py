import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from .base import BaseLongNameIdMixin
from .base import UserOwnedMixin

DocType = sa.Enum('markdown', 'html',
                  name='document_type_enum')


class BaseDocumentMixin(BaseLongNameIdMixin):
    @declared_attr
    def title(self):
        return sa.Column(sa.Unicode(500))

    @declared_attr
    def description(self):
        return sa.Column(sa.Unicode(500))

    @declared_attr
    def doctype(self):
        return sa.Column(DocType, default='markdown')

    @declared_attr
    def content(self):
        return sa.Column(sa.UnicodeText)


class SiteDocumentMixin(BaseDocumentMixin):
    @declared_attr
    def __tablename__(self):
        return 'site_documents'

    @declared_attr
    def category(self):
        return sa.Column(sa.Unicode(50), default='site')


class UserDocumentMixin(BaseDocumentMixin, UserOwnedMixin):
    @declared_attr
    def __tablename__(self):
        return 'user_documents'
