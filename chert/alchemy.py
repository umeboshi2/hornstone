from datetime import datetime, date


from sqlalchemy import Column
# column types
#from sqlalchemy import Integer, String, Unicode
#from sqlalchemy import UnicodeText
#from sqlalchemy import Boolean, Date, LargeBinary
#from sqlalchemy import PickleType
#from sqlalchemy import Enum
from sqlalchemy import DateTime
#from sqlalchemy import BigInteger

from sqlalchemy import func

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

# here is the common base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# http://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression
from sqlalchemy.sql import compiler
from psycopg2.extensions import adapt as sqlescape

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


class SerialBase(object):
    def serialize(self):
        data = dict()
        table = self.__table__
        for column in table.columns:
            name = column.name
            try:
                pytype = column.type.python_type
            except NotImplementedError:
                #print "NOTIMPLEMENTEDERROR", column.type
                continue
            value = getattr(self, name)
            if pytype is datetime or pytype is date:
                if value is not None:
                    value = value.isoformat()
            data[name] = value
        return data



class TimeStampMixin(SerialBase):
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    
    
def _make_db_session(dburl, create_all=False, baseclass=None):
    settings = {'sqlalchemy.url' : dburl}
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

