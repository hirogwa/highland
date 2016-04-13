import unittest
from unittest.mock import MagicMock
from highland import models


class TestShow(unittest.TestCase):
    def test_iter(self):
        user = MagicMock()
        user.id = 2
        show = models.Show(user, 'my title', 'my description')
        show.id = 1

        show_d = dict(show)

        self.assertEqual(4, len(show_d))
        self.assertEqual(show.owner_user_id, show_d.get('owner_user_id'))
        self.assertEqual(show.id, show_d.get('id'))
        self.assertEqual(show.title, show_d.get('title'))
        self.assertEqual(show.description, show_d.get('description'))
