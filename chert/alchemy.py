from datetime import datetime, date

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker


class SerialBase(object):
    def serialize(self):
        data = dict()
        table = self.__table__
        for column in table.columns:
            name = column.name
            try:
                pytype = column.type.python_type
            except NotImplementedError:
                print "NOTIMPLEMENTEDERROR", column.type
            value = getattr(self, name)
            if pytype is datetime or pytype is date:
                if value is not None:
                    value = value.isoformat()
            data[name] = value
        return data
    
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

