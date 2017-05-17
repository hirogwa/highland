import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from highland import show_operation, models, common
from highland.exception import AccessNotAllowedError, InvalidValueError, \
    NoSuchEntityError
from highland.models import Show


class TestShowOperation(unittest.TestCase):
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'add')
    @patch.object(common, 'is_valid_alias')
    def test_create(self, mock_valid_alias, mock_add, mock_commit):
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

        mock_valid_alias.return_value = True

        show_operation.create(
            user_id, title, description, subtitle, language, author,
            category, explicit, image_id, alias)

        mock_valid_alias.assert_called_with(alias)
        self.assertEqual(1, mock_add.call_count)
        self.assertEqual(1, mock_commit.call_count)

    @patch.object(common, 'is_valid_alias')
    def test_create_bad_alias(self, mock_valid_alias):
        mock_valid_alias.return_value = False
        with self.assertRaises(InvalidValueError):
            show_operation.create(*(MagicMock() for x in range(10)))

    @patch.object(models.db.session, 'commit')
    @patch.object(show_operation, 'get_model')
    def test_update(self, mock_get, mock_commit):
        show = Show(1, 'title', 'desc', 'subtitle', 'lang', 'author',
                    'category', False, 2, 'alias')

        mock_get.return_value = show
        show_operation.update(1, 3, 't', 'd', 's', 'l', 'a', 'c', True, 3)

        self.assertEqual(1, mock_commit.call_count)

    @patch.object(show_operation, 'get_model')
    def test_update_fails_if_show_is_not_owned_by_user(self, mock_get):
        show = Show(1, 'title', 'desc', 'subtitle', 'lang', 'author',
                    'category', False, 2, 'alias')
        mock_get.return_value = show
        with self.assertRaises(AccessNotAllowedError):
            show_operation.update(99, 1, 't', 'd', 's', 'l', 'a', 'c', True, 3)

    @patch.object(show_operation, 'get_model')
    def test_update_fails_if_show_does_not_exist(self, mock_get):
        mock_get.side_effect = NoSuchEntityError
        with self.assertRaises(NoSuchEntityError):
            show_operation.update(1, 2, 't', 'd', 's', 'l', 'a', 'c', True, 3)
        mock_get.assert_called_with(2)

    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'delete')
    @patch.object(show_operation, 'get_model')
    def test_delete(self, mock_get, mock_delete, mock_commit):
        show = Show(1, 'title', 'desc', 'subtitle', 'lang', 'author',
                    'category', False, 2, 'alias')
        mock_get.return_value = show

        result = show_operation.delete(1, 10)

        mock_delete.assert_called_with(show)
        mock_commit.assert_called_with()
        self.assertTrue(result)

    @patch.object(show_operation, 'get_model')
    def test_delete_fails_if_show_is_not_owned_by_user(self, mock_get):
        show = Show(1, 'title', 'desc', 'subtitle', 'lang', 'author',
                    'category', False, 2, 'alias')
        mock_get.return_value = show
        with self.assertRaises(AccessNotAllowedError):
            show_operation.delete(99, 1)

    @patch.object(show_operation, 'get_model')
    def test_delete_fails_if_show_does_not_exist(self, mock_get):
        mock_get.side_effect = NoSuchEntityError
        with self.assertRaises(NoSuchEntityError):
            show_operation.delete(1, 2)

    @patch('highland.show_operation.Show')
    def test_load(self, mock_show):
        show_a = Show(1, 'title', 'desc', 'subtitle', 'lang', 'author',
                      'category', False, 2, 'alias')
        show_b = Show(1, 't', 'd', 's', 'l', 'a', 'c', False, 2, 'a')
        l = [show_a, show_b]
        mock_show.query.filter_by.return_value.all.return_value = l

        result = show_operation.load(1)

        mock_show.query.filter_by.assert_called_with(owner_user_id=1)
        self.assertEqual([dict(x) for x in l], result)

    @patch.object(show_operation, 'get_model')
    def test_get(self, mock_get_model):
        show = Show(1, 't', 'd', 's', 'l', 'a', 'c', False, 2, 'a')
        show.id = 10
        mock_get_model.return_value = show

        result = show_operation.get(1, 10)

        self.assertEqual(dict(show), result)

    @patch.object(show_operation, 'get_model')
    def test_get_fails_if_show_is_not_owned_by_user(self, mock_get_model):
        show = Show(1, 't', 'd', 's', 'l', 'a', 'c', False, 2, 'a')
        show.id = 10
        mock_get_model.return_value = show

        with self.assertRaises(AccessNotAllowedError):
            show_operation.get(99, 10)

    @patch.object(show_operation, 'get_model')
    def test_get_fails_if_show_does_not_exist(self, mock_get_model):
        mock_get_model.side_effect = NoSuchEntityError
        with self.assertRaises(NoSuchEntityError):
            show_operation.get(99, 10)

    @patch('highland.show_operation.Show')
    def test_get_model(self, mock_show):
        show = Show(1, 't', 'd', 's', 'l', 'a', 'c', False, 2, 'a')
        show.id = 10

        self.assertFalse(hasattr(show, 'url'))
        mock_show.query.filter_by.return_value.first.return_value = show
        show_operation.get_model(10)
        self.assertIsNotNone(show.url)

    @patch('highland.show_operation.Show')
    def test_get_model_fails_if_show_does_not_exist(self, mock_show):
        mock_show.query.filter_by.return_value.first.return_value = None
        with self.assertRaises(NoSuchEntityError):
            show_operation.get_model(1)
