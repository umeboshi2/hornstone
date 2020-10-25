import unittest


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
