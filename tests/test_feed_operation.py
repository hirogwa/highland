import unittest
from feedgen.feed import FeedGenerator
from feedgen.ext.podcast import PodcastExtension
from unittest.mock import MagicMock
from highland import feed_operation, show_operation, episode_operation,\
    media_storage, audio_operation


class TestFeedOperation(unittest.TestCase):
    @unittest.mock.patch.object(feed_operation, '_format_seconds')
    @unittest.mock.patch.object(audio_operation, 'get_audio_url')
    @unittest.mock.patch.object(audio_operation, 'get_audio_or_assert')
    @unittest.mock.patch.object(FeedGenerator, 'add_entry')
    @unittest.mock.patch.object(FeedGenerator, 'rss_str')
    @unittest.mock.patch.object(PodcastExtension, 'itunes_summary')
    @unittest.mock.patch.object(PodcastExtension, 'itunes_subtitle')
    @unittest.mock.patch.object(PodcastExtension, 'itunes_owner')
    @unittest.mock.patch.object(PodcastExtension, 'itunes_explicit')
    @unittest.mock.patch.object(PodcastExtension, 'itunes_category')
    @unittest.mock.patch.object(PodcastExtension, 'itunes_author')
    @unittest.mock.patch.object(FeedGenerator, 'lastBuildDate')
    @unittest.mock.patch.object(FeedGenerator, 'language')
    @unittest.mock.patch.object(FeedGenerator, 'link')
    @unittest.mock.patch.object(FeedGenerator, 'description')
    @unittest.mock.patch.object(FeedGenerator, 'title')
    @unittest.mock.patch.object(media_storage, 'upload')
    @unittest.mock.patch.object(episode_operation, 'get_episode_url')
    @unittest.mock.patch.object(episode_operation, 'load')
    @unittest.mock.patch.object(show_operation, 'get_show_url')
    @unittest.mock.patch.object(show_operation, 'get_show_unique_id')
    @unittest.mock.patch.object(show_operation, 'get_show_or_assert')
    def test_update(
            self,
            mocked_get_show, mocked_unique_id, mocked_get_show_url,
            mocked_load_episode, mocked_get_episode_url,
            mocked_upload,
            mocked_fg_title, mocked_fg_description, mocked_fg_link,
            mocked_fg_language, mocked_fg_last_build_date,
            mocked_i_author, mocked_i_category, mocked_i_explicit,
            mocked_i_owner, mocked_i_subtitle, mocked_i_summary,
            mocked_fg_rss_str, mocked_fg_add_entry,
            mocked_get_audio, mocked_get_audio_url, mocked_format_seconds):
        mocked_user = MagicMock()
        mocked_show = MagicMock()
        mocked_show_url = MagicMock()
        mocked_episode = MagicMock()
        mocked_episode_url = MagicMock()
        mocked_content = MagicMock()
        mocked_audio = MagicMock()
        audio_url = 'some_audio_url'
        unique_id = 'someid'
        formatted_seconds = '0:25:12'
        mocked_fe = MagicMock()

        mocked_get_show.return_value = mocked_show
        mocked_get_show_url.return_value = mocked_show_url
        mocked_load_episode.return_value = [mocked_episode]
        mocked_get_episode_url.return_value = mocked_episode_url
        mocked_fg_rss_str.return_value = mocked_content
        mocked_unique_id.return_value = unique_id
        mocked_fg_add_entry.return_value = mocked_fe

        mocked_get_audio.return_value = mocked_audio
        mocked_get_audio_url.return_value = audio_url
        mocked_format_seconds.return_value = formatted_seconds

        feed_operation.update(mocked_user, mocked_show.id)

        mocked_get_show.assert_called_with(mocked_user, mocked_show.id)
        mocked_fg_title.assert_called_with(mocked_show.title)
        mocked_fg_description.assert_called_with(mocked_show.description)
        mocked_fg_link.assert_called_with(href=mocked_show_url)
        mocked_fg_language.assert_called_with(mocked_show.language)
        mocked_fg_last_build_date.assert_called_with(
            mocked_show.last_build_datetime)
        mocked_i_author.assert_called_with(mocked_show.author)
        mocked_i_category.assert_called_with(mocked_show.category)
        mocked_i_explicit.assert_called_with(
            'yes' if mocked_show.explicit else 'no')
        mocked_i_owner.assert_called_with(name=mocked_user.name,
                                          email=mocked_user.email)
        mocked_i_subtitle(mocked_show.subtitle)
        mocked_i_summary(mocked_show.description)

        mocked_fg_rss_str.assert_called_with(pretty=True)
        mocked_get_episode_url.assert_called_with(mocked_episode)
        mocked_fg_add_entry.assert_called_with()
        mocked_fe.title.assert_called_with(mocked_episode.title)
        mocked_fe.link.assert_called_with(href=mocked_episode_url)
        mocked_fe.description.assert_called_with(mocked_episode.description)
        mocked_fe.enclosure.assert_called_with(
            url=audio_url, length=str(mocked_audio.length),
            type=mocked_audio.type)
        mocked_fe.guid.assert_called_with(mocked_episode.guid)
        mocked_fe.pubdate.assert_called_with(mocked_episode.update_datetime)
        mocked_fe.podcast.itunes_author.\
            assert_called_with(mocked_show.author)
        mocked_fe.podcast.itunes_duration.\
            assert_called_with(formatted_seconds)
        mocked_fe.podcast.itunes_explicit.\
            assert_called_with('yes' if mocked_episode.explicit else 'no')
        mocked_fe.podcast.itunes_subtitle.\
            assert_called_with(mocked_episode.subtitle)

        mocked_upload.assert_called_with(
            mocked_content, unique_id, feed_operation.FEED_FOLDER_RSS,
            ContentType=feed_operation.FEED_CONTENT_TYPE)

    def test_format_seconds(self):
        self.assertEqual('0:00:09', feed_operation._format_seconds(9))
        self.assertEqual('0:09:19', feed_operation._format_seconds(559))
        self.assertEqual('12:12:09', feed_operation._format_seconds(43929))