import unittest


class GetbooleanTest(unittest.TestCase):
    def test_false_lower(self):
        from ..util import getboolean
        result = getboolean('false')
        expected = False
        self.assertEqual(result, expected)

    def test_false_title(self):
        from ..util import getboolean
        result = getboolean('False')
        expected = False
        self.assertEqual(result, expected)

    def test_false_upper(self):
        from ..util import getboolean
        result = getboolean('FALSE')
        expected = False
        self.assertEqual(result, expected)

    def test_yes_lower(self):
        from ..util import getboolean
        result = getboolean('yes')
        expected = True
        self.assertEqual(result, expected)

    def test_yes_title(self):
        from ..util import getboolean
        result = getboolean('Yes')
        expected = True
        self.assertEqual(result, expected)

    def test_yes_upper(self):
        from ..util import getboolean
        result = getboolean('YES')
        expected = True
        self.assertEqual(result, expected)

    def test_no_lower(self):
        from ..util import getboolean
        result = getboolean('no')
        expected = False
        self.assertEqual(result, expected)

    def test_no_title(self):
        from ..util import getboolean
        result = getboolean('No')
        expected = False
        self.assertEqual(result, expected)

    def test_no_upper(self):
        from ..util import getboolean
        result = getboolean('NO')
        expected = False
        self.assertEqual(result, expected)

    def test_getboolean(self):
        from ..util import getboolean
        result = getboolean('no')
        expected = False
        self.assertEqual(result, expected)


