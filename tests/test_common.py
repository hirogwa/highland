import unittest
from highland import common


class TestCommon(unittest.TestCase):
    def test_is_valid_alias(self):
        self.assertTrue(common.is_valid_alias('someAlias01'))
        self.assertTrue(common.is_valid_alias('some_Alias_01'))
        self.assertTrue(common.is_valid_alias('1234'))
        self.assertTrue(common.is_valid_alias('name'))
        self.assertTrue(common.is_valid_alias('NAME'))

        self.assertFalse(common.is_valid_alias(''))
        self.assertFalse(common.is_valid_alias('some-alias-01'))
