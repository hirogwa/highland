from flask import render_template
from highland import show_operation, episode_operation, media_storage, \
    settings, audio_operation, feed_operation


def update_full(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    episodes = episode_operation.load_public(user, show_id)
    home_url = '/{}'.format(show.alias)
    feed_url = feed_operation.get_feed_url(user, show_id)
    _update_show(user, show, episodes, home_url, feed_url)
    _delete_all_episodes(user, show)
    for episode in episodes:
        _update_episode(user, show, episode, home_url, feed_url)
    return True


def _update_show(user, show, episodes, home_url, feed_url, upload=True):
    html = render_template('public_sites/index.html',
                           title=show.title,
                           show=show,
                           home_url=home_url,
                           feed_url=feed_url,
                           episodes=episodes)
    if upload:
        media_storage.upload(html, settings.S3_BUCKET_SITES, show.alias,
                             ContentType='text/html; charset=utf-8')
    return html


def _update_episode(user, show, episode, home_url, feed_url, upload=True):
    audio = audio_operation.get_audio_or_assert(user, episode.audio_id)
    m, s = divmod(audio.duration, 60)
    h, m = divmod(m, 60)
    length = '{0:.2f}'.format(audio.length / 1000000)

    html = render_template(
        'public_sites/episode.html',
        title=episode.title,
        show=show,
        home_url=home_url,
        feed_url=feed_url,
        episode=episode,
        duration="%d:%02d:%02d" % (h, m, s),
        length=length,
        audio_url=audio_operation.get_audio_url(user, audio))
    if upload:
        media_storage.upload(
            html, settings.S3_BUCKET_SITES, episode.alias,
            show.alias, ContentType='text/html; charset=utf-8')
    return html


def _delete_all_episodes(user, show):
    media_storage.delete_folder(settings.S3_BUCKET_SITES, show.alias)
