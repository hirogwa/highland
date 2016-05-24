import unittest
from feedgen.feed import FeedGenerator
from feedgen.ext.podcast import PodcastExtension
from unittest.mock import MagicMock
from highland import feed_operation, show_operation, episode_operation,\
    media_storage, audio_operation, image_operation, settings


class TestFeedOperation(unittest.TestCase):
    @unittest.mock.patch.object(image_operation, 'get_image_url')
    @unittest.mock.patch.object(image_operation, 'get_image_or_assert')
    @unittest.mock.patch.object(feed_operation, '_format_seconds')
    @unittest.mock.patch.object(audio_operation, 'get_audio_url')
    @unittest.mock.patch.object(audio_operation, 'get_audio_or_assert')
    @unittest.mock.patch.object(FeedGenerator, 'add_entry')
    @unittest.mock.patch.object(FeedGenerator, 'rss_str')
    @unittest.mock.patch.object(PodcastExtension, 'itunes_image')
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
    @unittest.mock.patch.object(show_operation, 'get_show_or_assert')
    def test_update(
            self,
            mocked_get_show, mocked_get_show_url,
            mocked_load_episode, mocked_get_episode_url,
            mocked_upload,
            mocked_fg_title, mocked_fg_description, mocked_fg_link,
            mocked_fg_language, mocked_fg_last_build_date,
            mocked_i_author, mocked_i_category, mocked_i_explicit,
            mocked_i_owner, mocked_i_subtitle, mocked_i_summary,
            mocked_i_image,
            mocked_fg_rss_str, mocked_fg_add_entry,
            mocked_get_audio, mocked_get_audio_url, mocked_format_seconds,
            mocked_get_image, mocked_get_image_url):
        mocked_user = MagicMock()
        mocked_show = MagicMock()
        mocked_show.image_id = 1
        image_url_show = 'some_url_show_image'
        mocked_show_url = MagicMock()
        mocked_episode = MagicMock()
        mocked_episode.image_id = 2
        image_url_episode = 'some_url_episode_image'
        mocked_episode_url = MagicMock()
        mocked_content = MagicMock()
        mocked_audio = MagicMock()
        audio_url = 'some_audio_url'
        formatted_seconds = '0:25:12'
        mocked_fe = MagicMock()
        mocked_image_show = MagicMock()
        mocked_image_episode = MagicMock()

        mocked_get_show.return_value = mocked_show
        mocked_get_show_url.return_value = mocked_show_url
        mocked_load_episode.return_value = [mocked_episode]
        mocked_get_episode_url.return_value = mocked_episode_url
        mocked_fg_rss_str.return_value = mocked_content
        mocked_fg_add_entry.return_value = mocked_fe

        mocked_get_audio.return_value = mocked_audio
        mocked_get_audio_url.return_value = audio_url
        mocked_format_seconds.return_value = formatted_seconds

        def get_image_side_effect(user, image_id):
            if image_id == mocked_show.image_id:
                return mocked_image_show
            elif image_id == mocked_episode.image_id:
                return mocked_image_episode
            assert False
        mocked_get_image.side_effect = get_image_side_effect

        def get_image_url_side_effect(image):
            if image == mocked_image_show:
                return image_url_show
            elif image == mocked_image_episode:
                return image_url_episode
            assert False
        mocked_get_image_url.side_effect = get_image_url_side_effect

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
        mocked_i_subtitle.assert_called_with(mocked_show.subtitle)
        mocked_i_summary.assert_called_with(mocked_show.description)
        mocked_get_image.assert_any_call(mocked_user, mocked_show.image_id)
        mocked_i_image.assert_called_with(image_url_show)

        mocked_fg_rss_str.assert_called_with(pretty=True)
        mocked_get_episode_url.assert_called_with(mocked_user, mocked_episode,
                                                  mocked_show)
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
        mocked_get_image.assert_any_call(mocked_user, mocked_episode.image_id)
        mocked_fe.podcast.itunes_image.assert_called_with(image_url_episode)

        mocked_upload.assert_called_with(
            mocked_content, settings.S3_BUCKET_FEED, mocked_show.alias,
            feed_operation.FEED_FOLDER_RSS,
            ContentType=feed_operation.FEED_CONTENT_TYPE)

    def test_format_seconds(self):
        self.assertEqual('0:00:09', feed_operation._format_seconds(9))
        self.assertEqual('0:09:19', feed_operation._format_seconds(559))
        self.assertEqual('12:12:09', feed_operation._format_seconds(43929))
