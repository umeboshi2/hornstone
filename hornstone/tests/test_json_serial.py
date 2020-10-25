import unittest


class GetbooleanTest(unittest.TestCase):
    def _test_methods(self, value, expected):
        from ..util import getboolean
        methods = ['lower', 'title', 'upper']
        for method in methods:
            test_value = getattr(value, method)()
            params = dict(test_value=test_value,
                          method=method,
                          value=value,
                          expected=expected)
            msg = "value is {}, expected result {}".format(value, expected)
            with self.subTest(msg, **params):
                result = getboolean(test_value)
                self.assertEqual(result, expected)

    def test_truthness(self):
        values = ['true', 'yes', '1', 'on']
        for value in values:
            self._test_methods(value, True)

    def test_falseness(self):
        values = ['false', 'no', '0', 'off']
        for value in values:
            self._test_methods(value, False)

    def test_bad_values(self):
        from ..util import getboolean
        values = ['f', 't', 'y', 'n', '2']
        for value in values:
            msg = "value is {}".format(value)
            with self.subTest(msg=msg, value=value):
                self.assertRaises(ValueError, getboolean, value)

    def test_bad_types(self):
        from ..util import getboolean
        values = [0, 1, 2, 0.0, True, False]
        for value in values:
            msg = "value is {}".format(value)
            with self.subTest(msg=msg, value=value):
                self.assertRaises(AttributeError, getboolean, value)


class JSONSerialTest(unittest.TestCase):
    def test_date(self):
        # from ..util import json_serial
        # from datetime import date
        pass
