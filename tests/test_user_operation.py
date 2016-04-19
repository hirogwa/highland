import unittest
from unittest.mock import MagicMock
from highland import user_operation


class TestUserOperation(unittest.TestCase):
    @unittest.mock.patch('highland.models.User.query')
    def test_get_id(self, mocked_query):
        mocked_user = MagicMock()
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_user
        mocked_query.filter_by.return_value = mocked_filter
        id = 1

        result = user_operation.get(id)

        mocked_query.filter_by.assert_called_with(id=id)
        mocked_filter.first.assert_called_with()
        self.assertEqual(mocked_user, result)

    @unittest.mock.patch('highland.models.User.query')
    def test_get_id_not_found(self, mocked_query):
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter
        id = 1

        with self.assertRaises(AssertionError):
            user_operation.get(id)
        mocked_query.filter_by.assert_called_with(id=id)
        mocked_filter.first.assert_called_with()

    @unittest.mock.patch('highland.models.User.query')
    def test_get_credentials(self, mocked_query):
        mocked_user = MagicMock()
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_user
        mocked_query.filter_by.return_value = mocked_filter
        username = 'somename'
        password = 'somepass'

        result = user_operation.get(username=username, password=password)

        mocked_query.filter_by.assert_called_with(
            username=username, password=password)
        mocked_filter.first.assert_called_with()
        self.assertEqual(mocked_user, result)

    @unittest.mock.patch('highland.models.User.query')
    def test_get_credentials_not_found(self, mocked_query):
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter
        username = 'somename'
        password = 'somepass'

        with self.assertRaises(AssertionError):
            user_operation.get(username=username, password=password)
        mocked_query.filter_by.assert_called_with(
            username=username, password=password)
        mocked_filter.first.assert_called_with()

    def test_get_credentials_lacking_username(self):
        with self.assertRaises(ValueError):
            user_operation.get(username='someuser')

    def test_user_credentials_lacking_password(self):
        with self.assertRaises(ValueError):
            user_operation.get(password='somepass')
