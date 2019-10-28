import unittest


def init_user_database(engine):
    from ..alchemy import Base
    from ..models.usergroup import UserMixin, GroupMixin, UserGroupMixin

    class User(Base, UserMixin):
        pass

    class Group(Base, GroupMixin):
        pass

    class GroupUser(Base, UserGroupMixin):
        pass
    models = dict(User=User,
                  Group=Group, GroupUser=GroupUser)
    Base.metadata.create_all(engine)
    return models


class ChunksTest(unittest.TestCase):
    def test_chunks1(self):
        from ..base import chunks
        result = list(chunks(b'abcdefghi', 4))
        expected = [b'abcd', b'efgh', b'i']
        self.assertEqual(result, expected)

    def test_chunks2(self):
        from ..base import chunks
        result = list(chunks(b'abcdefghi', 3))
        expected = [b'abc', b'def', b'ghi']
        self.assertEqual(result, expected)


class BaseAlchemyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from sqlalchemy import engine_from_config
        from sqlalchemy.orm import sessionmaker
        settings = {'sqlalchemy.url': 'sqlite:///:memory:'}
        cls.engine = engine_from_config(settings, 'sqlalchemy.')
        factory = sessionmaker()
        factory.configure(bind=cls.engine)
        cls.session = factory()

    @classmethod
    def tearDownClass(cls):
        from ..alchemy import Base
        Base.metadata.drop_all(cls.engine)


class BaseUserGroupTest(BaseAlchemyTest):
    @classmethod
    def setUpClass(cls):
        super(BaseUserGroupTest, cls).setUpClass()
        cls.models = init_user_database(cls.engine)

    @classmethod
    def tearDownClass(cls):
        from ..alchemy import Base
        Base.metadata.drop_all(cls.engine)


class SimpleUserTest(BaseUserGroupTest):
    @classmethod
    def setUpClass(cls):
        super(SimpleUserTest, cls).setUpClass()
        user = cls.models['User']()
        user.username = 'admin'
        cls.session.add(user)
        cls.session.commit()

    def test_user_created(self):
        User = self.models['User']
        user = self.session.query(User).filter_by(username='admin').first()
        self.assertEqual(user.username, 'admin')

    def test_user_id(self):
        from uuid import UUID
        User = self.models['User']
        user = self.session.query(User).filter_by(username='admin').first()
        result = type(user.id)
        expected = UUID
        self.assertEqual(result, expected)
