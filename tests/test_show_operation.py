import unittest
from unittest.mock import MagicMock
from highland import show_operation, models


class TestShowOperation(unittest.TestCase):
    @unittest.mock.patch('highland.models.Show')
    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    def test_create(self, mocked_add, mocked_commit, mocked_show_class):
        mocked_user = MagicMock()
        title = 'my show'
        description = 'my show description'

        mocked_show = MagicMock()
        mocked_show_class.return_value = mocked_show

        result = show_operation.create(mocked_user, title, description)

        mocked_show_class.assert_called_with(mocked_user, title, description)
        mocked_add.assert_called_with(mocked_show)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_show, result)
