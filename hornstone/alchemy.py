import io
import lzma
import json
from uuid import UUID

import warnings
from datetime import datetime, date

import sqlalchemy as sa
from sqlalchemy import PickleType

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

# here is the common base from pyramid alchemy template
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from sqlalchemy_utils import Timestamp

# http://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression
from sqlalchemy.sql import compiler
from psycopg2.extensions import adapt as sqlescape
import transaction


def compile_query(query):
    dialect = query.session.bind.dialect
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    comp.compile()
    enc = dialect.encoding
    params = {}
    for k, v in comp.params.items():
        if isinstance(v, str):
            v = v.encode(enc)
        params[k] = sqlescape(v)
    return (comp.string.encode(enc) % params).decode(enc)


# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


# inspired by ziggurat_foundations
class BaseModel(object):
    @classmethod
    def _get_keys(cls):
        'returns column names for this model'
        return sa.orm.class_mapper(cls).c.keys()

    @classmethod
    def get_primary_key(cls):
        'returns primary key'
        return sa.orm.class_mapper(cls).primary_key

    def to_dict(self):
        data = {}
        for key in self._get_keys():
            data[key] = getattr(self, key)
        return data

    def get_table_column_names(self):
        return self._get_keys()


class SerialBase(BaseModel):
    def serialize(self):
        data = dict()
        table = self.__table__
        for column in table.columns:
            name = column.name
            try:
                pytype = column.type.python_type
            except NotImplementedError:
                if type(column.type) is PickleType:
                    value = getattr(self, name)
                    if type(value) not in [dict, list]:
                        # ignore column
                        continue
                else:
                    msg = "{}({}) Not Implemented.".format(column, column.type)
                    warnings.warn(msg)
                    continue
            value = getattr(self, name)
            if pytype is datetime or pytype is date:
                if value is not None:
                    value = value.isoformat()
            elif pytype is UUID:
                if value is not None:
                    value = str(value)
            data[name] = value
        return data


class TimeStampMixin(SerialBase, Timestamp):
    @property
    def created_at(self):
        warnings.warn("created_at no longer needed")
        return super(Timestamp, self).created

    @property
    def updated_at(self):
        warnings.warn("updated_at no longer needed")
        return super(Timestamp, self).updated


def _make_db_session(dburl, create_all=False, baseclass=None):
    settings = {'sqlalchemy.url': dburl}
    engine = engine_from_config(settings)
    if create_all:
        baseclass.metadata.create_all(engine)
    session_class = sessionmaker()
    session_class.configure(bind=engine)
    return session_class


def make_sqlite_session(filename, create_all=False, baseclass=None):
    dburl = "sqlite:///%s" % filename
    return _make_db_session(dburl, create_all=create_all,
                            baseclass=baseclass)


def make_postgresql_session(dburl, create_all=False, baseclass=None):
    return _make_db_session(dburl, create_all=create_all,
                            baseclass=baseclass)


# This can use a lot of memory.  This is only useful for
# smaller datasets.
def export_models(session, models):
    data = dict()
    output = io.BytesIO()
    with transaction.manager:
        with lzma.LZMAFile(output, 'w') as zfile:
            for model in models:
                q = session.query(model)
                name = model.__name__
                print("Dumping {}".format(name))
                mlist = [m.serialize() for m in q]
                data[name] = mlist
                print("Exported {}".format(name))
            content = json.dumps(data).encode()
            zfile.write(content)
    del data
    return output.getvalue()
