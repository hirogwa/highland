import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from highland import show_operation, models, common, exception, settings
from highland.exception import InvalidValueError


class TestShowOperation(unittest.TestCase):
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'add')
    @patch.object(common, 'is_valid_alias')
    def test_create(self, mocked_valid_alias, mocked_add, mocked_commit):
        user_id = 1
        title = 'my show'
        description = 'my show description'
        subtitle = 'my show subtitle'
        language = 'en-US'
        author = 'Ultraman Taro, Ultraman Ace'
        category = 'Technology'
        explicit = False
        image_id = 2
        alias = 'ultraSpaceShow'

        mocked_valid_alias.return_value = True

        show_operation.create(
            user_id, title, description, subtitle, language, author,
            category, explicit, image_id, alias)

        mocked_valid_alias.assert_called_with(alias)
        self.assertEqual(1, mocked_add.call_count)
        self.assertEqual(1, mocked_commit.call_count)

    @unittest.mock.patch.object(common, 'is_valid_alias')
    def test_create_bad_alias(self, mocked_valid_alias):
        mocked_valid_alias.return_value = False
        with self.assertRaises(InvalidValueError):
            show_operation.create(*(MagicMock() for x in range(10)))

    @unittest.mock.patch('highland.models.Show.query')
    @unittest.mock.patch.object(models.db.session, 'commit')
    def test_update(self, mocked_commit, mocked_query):
        owner_user_id = 1
        show_id = 2

        mocked_user = MagicMock()
        mocked_user.id = owner_user_id

        mocked_show = MagicMock()
        mocked_show.owner_user_id = owner_user_id
        mocked_show.id = show_id

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_show
        mocked_query.filter_by.return_value = mocked_filter

        title = 'title new'
        description = 'desc new'
        subtitle = 'subtitle new'
        language = 'en-US'
        author = 'Ultra Seven, Ultraman Jack'
        category = 'Arts'
        explicit = False
        image_id = 2

        result = show_operation.update(
            mocked_user, show_id, title, description, subtitle, language,
            author, category, explicit, image_id)

        mocked_query.filter_by.assert_called_with(id=show_id)
        mocked_filter.first.assert_called_with()
        mocked_commit.assert_called_with()
        self.assertEqual(title, mocked_show.title)
        self.assertEqual(description, mocked_show.description)
        self.assertEqual(subtitle, mocked_show.subtitle)
        self.assertEqual(language, mocked_show.language)
        self.assertEqual(author, mocked_show.author)
        self.assertEqual(category, mocked_show.category)
        self.assertEqual(explicit, mocked_show.explicit)
        self.assertEqual(image_id, mocked_show.image_id)
        self.assertEqual(result, mocked_show)

    @unittest.mock.patch('highland.models.Show.query')
    @unittest.mock.patch.object(models.db.session, 'commit')
    def test_update_assert_non_existing(self, mocked_commit, mocked_query):
        owner_user_id = 1
        show_id = 2
        mocked_user = MagicMock()
        mocked_user.id = owner_user_id

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(exception.NoSuchEntityError):
            show_operation.update(
                mocked_user, show_id, 'title', 'desc', 'subtitle', 'lang',
                'author', 'category', False, 2)

        mocked_query.filter_by.assert_called_with(id=show_id)
        mocked_filter.first.assert_called_with()
        mocked_commit.assert_not_called()

    @unittest.mock.patch.object(models.db.session, 'commit')
    @unittest.mock.patch.object(models.db.session, 'delete')
    def test_delete(self, mocked_delete, mocked_commit):
        mocked_show = MagicMock()

        result = show_operation.delete(mocked_show)

        mocked_delete.assert_called_with(mocked_show)
        mocked_commit.assert_called_with()
        self.assertTrue(result)

    @unittest.mock.patch('highland.models.Show.query')
    def test_load(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1

        mocked_show_01 = MagicMock()
        mocked_show_02 = MagicMock()
        show_list = [mocked_show_01, mocked_show_02]

        mocked_filter = MagicMock()
        mocked_filter.all.return_value = show_list
        mocked_query.filter_by.return_value = mocked_filter

        result = show_operation.load(mocked_user)

        mocked_query.filter_by.assert_called_with(owner_user_id=mocked_user.id)
        mocked_filter.all.assert_called_with()
        self.assertEqual(show_list, result)

    @unittest.mock.patch('highland.models.Show.query')
    def test_get_show_or_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        mocked_show = MagicMock()
        mocked_show.owner_user_id = mocked_user.id
        mocked_show.id = 2

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = mocked_show
        mocked_query.filter_by.return_value = mocked_filter

        result = show_operation.get_show_or_assert(
            mocked_user, mocked_show.id)

        mocked_query.filter_by.assert_called_with(id=mocked_show.id)
        mocked_filter.first.assert_called_with()
        self.assertEqual(result, mocked_show)

    @unittest.mock.patch('highland.models.Show.query')
    def test_get_show_or_assert_assert(self, mocked_query):
        mocked_user = MagicMock()
        mocked_user.id = 1
        show_id = 2

        mocked_filter = MagicMock()
        mocked_filter.first.return_value = None
        mocked_query.filter_by.return_value = mocked_filter

        with self.assertRaises(exception.NoSuchEntityError):
            show_operation.get_show_or_assert(
                mocked_user, show_id)

    def test_get_show_url(self):
        mocked_show = MagicMock()
        mocked_show.alias = 'some_alias'
        result = show_operation.get_show_url(mocked_show)
        self.assertEqual('{}/some_alias'.format(settings.HOST_SITE), result)

    def test_access_allowed_or_raise(self):
        user_id = 1
        mocked_show = MagicMock()
        mocked_show.owner_user_id = 2

        with self.assertRaises(exception.AccessNotAllowedError):
            show_operation.access_allowed_or_raise(user_id, mocked_show)
