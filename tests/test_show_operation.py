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
        subtitle = 'my show subtitle'
        language = 'en-US'
        author = 'Ultraman Taro, Ultraman Ace'
        category = 'Technology'
        explicit = False
        image_id = 2
        alias = 'ultra-space-show'

        mocked_show = MagicMock()
        mocked_show_class.return_value = mocked_show

        result = show_operation.create(
            mocked_user, title, description, subtitle, language, author,
            category, explicit, image_id, alias)

        mocked_show_class.assert_called_with(
            mocked_user, title, description, subtitle, language, author,
            category, explicit, image_id, alias)
        mocked_add.assert_called_with(mocked_show)
        mocked_commit.assert_called_with()
        self.assertEqual(mocked_show, result)

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

        mocked_query.filter_by.assert_called_with(owner_user_id=owner_user_id,
                                                  id=show_id)
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

        with self.assertRaises(AssertionError):
            show_operation.update(
                mocked_user, show_id, 'title', 'desc', 'subtitle', 'lang',
                'author', 'category', False, 2)

        mocked_query.filter_by.assert_called_with(owner_user_id=owner_user_id,
                                                  id=show_id)
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

        mocked_query.filter_by.assert_called_with(owner_user_id=mocked_user.id,
                                                  id=mocked_show.id)
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

        with self.assertRaises(AssertionError):
            show_operation.get_show_or_assert(
                mocked_user, show_id)
