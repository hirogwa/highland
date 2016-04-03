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

    @unittest.mock.patch.object(models.db.session, 'commit')
    def test_update(self, mocked_commit):
        owner_user_id = 1

        mocked_show = MagicMock()
        mocked_show.owner_user_id = owner_user_id
        mocked_show.title = 'title original'
        mocked_show.description = 'desc original'

        title = 'title new'
        description = 'desc new'

        result = show_operation.update(mocked_show, title, description)

        mocked_commit.assert_called_with()
        self.assertEqual(owner_user_id, mocked_show.owner_user_id)
        self.assertEqual(title, mocked_show.title)
        self.assertEqual(description, mocked_show.description)
        self.assertEqual(result, mocked_show)

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'delete')
    def test_delete(self, mocked_delete, mocked_commit):
        mocked_show = MagicMock()

        result = show_operation.delete(mocked_show)

        mocked_delete.assert_called_with(mocked_show)
        mocked_commit.assert_called_with()
        self.assertTrue(result)
