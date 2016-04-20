import unittest
from unittest.mock import MagicMock
from highland import user_operation, models


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

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    @unittest.mock.patch('highland.models.User')
    def test_signup(self, mocked_user_class, mocked_add, mocked_commit):
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_user_class.query.filter_by.return_value = mocked_filter

        mocked_user = MagicMock()
        mocked_user_class.return_value = mocked_user

        username = 'some username'
        email = 'some@example.com'
        password = 'some strong password'

        result = user_operation.signup(username, email, password)

        mocked_add.assert_called_with(mocked_user)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_user, result)

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'add')
    @unittest.mock.patch('highland.models.User.query')
    def test_signup_dupl_username(self, mocked_query,
                                  mocked_add, mocked_commit):
        username = 'some user'
        mocked_user = MagicMock()
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_user
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(AssertionError):
            user_operation.signup(username, 'some@example.com', 'some pass')
        mocked_query.filter_by.assert_called_with(username=username)
        mocked_filter.first.assert_called_with()
        mocked_add.assert_not_called()
        mocked_commit.assert_not_called()

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch('highland.models.User.query')
    def test_update(self, mocked_query, mocked_commit):
        id_original = 1
        username_original = 'original name'
        email_original = 'original@example.com'
        password_original = 'original pass'

        mocked_user = MagicMock()
        mocked_user.id = id_original
        mocked_user.username = username_original
        mocked_user.email = email_original
        mocked_user.password = password_original

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_user
        mocked_query.filter_by.return_value = mocked_filter

        username = 'some username'
        email = 'some@example.com'
        password = 'some pass'

        result = user_operation.update(id_original, username, email, password)

        mocked_query.filter_by.assert_called_with(id=id_original)
        mocked_filter.first.assert_called_with()
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_user, result)
        self.assertEqual(id_original, result.id)
        self.assertEqual(username, result.username)
        self.assertEqual(email, result.email)
        self.assertEqual(password, result.password)

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch('highland.models.User.query')
    def test_update_no_user(self, mocked_query, mocked_commit):
        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter
        id = 1
        with self.assertRaises(AssertionError):
            user_operation.update(id, 'username', 'some@example.com', 'pass')
        mocked_query.filter_by.assert_called_with(id=id)
        mocked_filter.first.assert_called_with()
        mocked_commit.assert_not_called()
