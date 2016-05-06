from feedgen.feed import FeedGenerator
from highland import show_operation, episode_operation, models, media_storage

FEED_FOLDER_RSS = 'feed_rss'
FEED_CONTENT_TYPE = 'application/rss+xml'


def update(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    fg = FeedGenerator()
    fg.title(show.title)
    fg.subtitle(show.description)
    fg.link(href=show_operation.get_show_url(show))

    for episode in episode_operation.load(
            user, show_id,
            draft_status=models.Episode.DraftStatus.published.name):
        fe = fg.add_entry()
        fe.title(episode.title)
        fe.link(href=episode_operation.get_episode_url(episode))
        fe.description(episode.description)

    return media_storage.upload(
        fg.rss_str(pretty=True), show_operation.get_show_unique_id(show),
        FEED_FOLDER_RSS, ContentType=FEED_CONTENT_TYPE)
