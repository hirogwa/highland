from feedgen.feed import FeedGenerator
from highland import show_operation, episode_operation, models, media_storage,\
    audio_operation

FEED_FOLDER_RSS = 'feed_rss'
FEED_CONTENT_TYPE = 'application/rss+xml'


def update(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    fg = FeedGenerator()
    fg.title(show.title)
    fg.description(show.description)
    fg.link(href=show_operation.get_show_url(show))
    fg.language(show.language)
    fg.lastBuildDate(show.last_build_datetime)

    fg.load_extension('podcast')
    fg.podcast.itunes_author(show.author)
    fg.podcast.itunes_category(show.category)
    fg.podcast.itunes_explicit('yes' if show.explicit else 'no')
    fg.podcast.itunes_owner(name=user.name, email=user.email)
    fg.podcast.itunes_subtitle(show.subtitle)
    fg.podcast.itunes_summary(show.description)

    for episode in episode_operation.load(
            user, show_id,
            draft_status=models.Episode.DraftStatus.published.name):
        audio = audio_operation.get_audio_or_assert(user, episode.audio_id)
        fe = fg.add_entry()
        fe.title(episode.title)
        fe.link(href=episode_operation.get_episode_url(episode))
        fe.description(episode.description)
        fe.enclosure(url=audio_operation.get_audio_url(audio),
                     length=str(audio.length), type=audio.type)
        fe.guid(episode.guid)
        fe.pubdate(episode.update_datetime or episode.create_datetime)

        fe.podcast.itunes_author(show.author)
        fe.podcast.itunes_duration(_format_seconds(audio.duration))
        fe.podcast.itunes_explicit('yes' if episode.explicit else 'no')
        fe.podcast.itunes_subtitle(episode.subtitle)

    return media_storage.upload(
        fg.rss_str(pretty=True), show_operation.get_show_unique_id(show),
        FEED_FOLDER_RSS, ContentType=FEED_CONTENT_TYPE)


def _format_seconds(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)
