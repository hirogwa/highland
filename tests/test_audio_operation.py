import unittest
from unittest.mock import patch, MagicMock
from highland import audio_operation, models, media_storage, settings, \
    exception
from highland.exception import AccessNotAllowedError
from highland.models import Audio, User


class TestAudioOperation(unittest.TestCase):
    @patch.object(models.db.session, 'commit')
    @patch.object(models.db.session, 'add')
    @patch('uuid.uuid4')
    def test_create(self, mock_uuid4, mock_add, mock_commit):
        mock_uuid4.return_value.hex = 'some_guid'

        result = audio_operation.create(1, 'some.mp3', 120, 6400, 'audio/mpeg')

        self.assertEqual(1, mock_add.call_count)
        mock_commit.assert_called_with()
        self.assertEqual(1, result.get('owner_user_id'))
        self.assertEqual('some_guid', result.get('guid'))

    @patch.object(media_storage, 'delete')
    @patch.object(models.db, 'session')
    def test_delete(self, mock_session, mock_delete):
        audios = [
            Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01'),
            Audio(1, 'file_two', 60, 256, 'audio/mpeg', 'some_guid_02')
        ]
        self._delete_prep(mock_session, audios)

        audio_operation.delete(1, [x.id for x in audios])

        self.assertEqual(2, mock_delete.call_count)
        mock_session.commit.assert_called_with()

    @patch.object(media_storage, 'delete')
    @patch.object(models.db, 'session')
    def test_delete_raises_when_audio_is_not_owned_by_the_user(
            self, mock_session, mock_delete):
        audios = [
            Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01'),
            Audio(9, 'file_two', 60, 256, 'audio/mpeg', 'some_guid_02')
        ]
        self._delete_prep(mock_session, audios)

        with self.assertRaises(AccessNotAllowedError):
            audio_operation.delete(9, [x.id for x in audios])

        mock_delete.assert_not_called()
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch.object(media_storage, 'delete')
    @patch.object(models.db, 'session')
    def test_delete_db_record_is_not_deleted_when_storage_error(
            self, mock_session, mock_delete):
        audio = Audio(1, 'file_one', 30, 128, 'audio/mpeg', 'some_guid_01')
        self._delete_prep(mock_session, [audio])
        mock_delete.side_effect = ValueError

        audio_operation.delete(1, [audio.id])

        self.assertEqual(1, mock_delete.call_count)
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_called_with()

    def _delete_prep(self, mock_session, audios):
        audio_id_base = 10
        for x in audios:
            x.id = audio_id_base
            audio_id_base += 1

        def create_user(audio):
            user = User('username', 'name', 'identity')
            user.id = id
            return user

        audio_ids = [x.id for x in audios]
        users = [create_user(audio) for audio in audios]
        mock_session.query(Audio, User).join(User). \
            filter(Audio.id.in_(audio_ids)).order_by(Audio.owner_user_id). \
            all.return_value = [(x, y) for x, y in zip(audios, users)]

    @patch.object(audio_operation, 'get_audio_url')
    @patch('highland.models.Episode.query')
    @patch('highland.models.Audio.query')
    def test_load(
            self, mock_query_audio, mock_query_episode, mock_get_url):
        mock_user = MagicMock()
        mock_user.id = 1

        mock_filter_audio = MagicMock()
        mock_audio_01, mock_audio_02, mock_audio_03 = \
            MagicMock(), MagicMock(), MagicMock()
        mock_audio_01.id = 11    # used
        mock_audio_02.id = 12    # used but whitelisted
        mock_audio_03.id = 13    # not used
        mock_audio_01.__iter__.return_value = iter({'id': 11})
        mock_audio_02.__iter__.return_value = iter({'id': 12})
        mock_audio_03.__iter__.return_value = iter({'id': 13})
        mock_filter_audio.all.return_value = [
            mock_audio_01, mock_audio_02, mock_audio_03]
        mock_query_audio.filter_by.return_value = mock_filter_audio

        mock_filter_episode = MagicMock()
        mock_episode_01, mock_episode_02, mock_episode_03 = \
            MagicMock(), MagicMock(), MagicMock()
        mock_episode_01.audio_id = 11    # used
        mock_episode_02.audio_id = 12    # used but whitelisted
        mock_episode_03.audio_id = None  # not used
        mock_episode_01.id = 21
        mock_episode_02.id = 22
        mock_episode_03.id = 23
        mock_filter_episode.all.return_value = [
            mock_episode_01, mock_episode_02, mock_episode_03]
        mock_query_episode.filter_by.return_value = mock_filter_episode

        result = audio_operation.load(mock_user, True, 12)

        mock_query_audio.filter_by.assert_called_with(
            owner_user_id=mock_user.id)
        mock_filter_audio.all.assert_called_with()
        mock_query_episode.filter_by.assert_called_with(
            owner_user_id=mock_user.id)
        mock_filter_episode.all.assert_called_with()
        self.assertEqual(2, len(result))
        self.assertEqual([22, None], [x['episode_id'] for x in result])

    @patch.object(audio_operation, 'access_allowed_or_raise')
    @patch('highland.models.Audio.query')
    def test_get_audio_or_assert(self, mock_query, mock_access):
        mock_user, mock_audio = MagicMock(), MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_audio
        mock_query.filter_by.return_value = mock_filter

        result = audio_operation.get_audio_or_assert(
            mock_user, mock_audio.id)

        mock_query.filter_by.assert_called_with(
            owner_user_id=mock_user.id, id=mock_audio.id)
        mock_filter.first.assert_called_with()
        mock_access.assert_called_with(mock_user.id, mock_audio)
        self.assertEqual(result, mock_audio)

    @patch.object(audio_operation, 'access_allowed_or_raise')
    @patch('highland.models.Audio.query')
    def test_get_audio_or_assert_not_found(self, mock_query, mock_access):
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter

        with self.assertRaises(exception.NoSuchEntityError):
            audio_operation.get_audio_or_assert(MagicMock(), 1)
        mock_access.assert_not_called()

    @patch.object(audio_operation, 'access_allowed_or_raise')
    def test_get_audio_url(self, mock_access):
        mock_user, mock_audio = MagicMock(), MagicMock()
        mock_user.identity_id = 'identity_id'
        mock_audio.guid = 'someguid'

        result = audio_operation.get_audio_url(mock_user, mock_audio)

        mock_access.assert_called_with(mock_user.id, mock_audio)
        self.assertEqual(
            '{}/identity_id/someguid'.format(settings.HOST_AUDIO), result)

    def test_access_allowed_or_raise(self):
        mock_audio = MagicMock()
        mock_audio.owner_user_id = 1
        result = audio_operation.access_allowed_or_raise(1, mock_audio)
        self.assertEqual(mock_audio, result)

    def test_access_allowed_or_raise_raise(self):
        mock_audio = MagicMock()
        mock_audio.owner_user_id = 2
        with self.assertRaises(exception.AccessNotAllowedError):
            audio_operation.access_allowed_or_raise(1, mock_audio)
