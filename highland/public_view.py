from flask import render_template
from highland import show_operation, episode_operation, media_storage, \
    settings, audio_operation, feed_operation, image_operation


def update_full(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    show_image = image_operation.get_image_or_assert(user, show.image_id) \
        if show.image_id else None
    episodes = episode_operation.load_public(user, show_id)
    show_html(user, show, show_image, episodes)
    _delete_all_episodes(user, show)
    for episode in episodes:
        episode_html(user, show, show_image, episode)
    return True


def show_html(user, show, show_image, episodes, upload=True):
    image_url = image_operation.get_image_url(user, show_image) \
        if show_image else ''
    html = render_template(
        'public_sites/index.html',
        title=show.title,
        show=show,
        url=show_operation.get_show_url(show),
        home_url=_get_site_url(show.alias),
        feed_url=feed_operation.get_feed_url(user, show),
        image_url=image_url,
        episodes=episodes)
    if upload:
        media_storage.upload(html, settings.S3_BUCKET_SITES, show.alias,
                             ContentType='text/html; charset=utf-8')
    return html


def episode_html(user, show, show_image, episode, upload=True):
    if episode.image_id is None:
        image_url = image_operation.get_image_url(user, show_image)
    else:
        ep_image = image_operation.get_image_or_assert(user, episode.image_id)
        image_url = image_operation.get_image_url(user, ep_image)

    if episode.audio_id:
        audio = audio_operation.get_audio_or_assert(user, episode.audio_id)
        m, s = divmod(audio.duration, 60)
        h, m = divmod(m, 60)
        length = '{0:.2f}'.format(audio.length / 1000000)
        audio_url = audio_operation.get_audio_url(user, audio)
    else:
        length = '0'
        h, m, s = 0, 0, 0
        # TODO causes console error
        audio_url = ''

    html = render_template(
        'public_sites/episode.html',
        title=episode.title,
        show=show,
        url=episode_operation.get_episode_url(user, episode),
        home_url=_get_site_url(show.alias),
        feed_url=feed_operation.get_feed_url(user, show),
        episode=episode,
        duration="%d:%02d:%02d" % (h, m, s),
        length=length,
        audio_url=audio_url,
        image_url=image_url)
    if upload:
        media_storage.upload(
            html, settings.S3_BUCKET_SITES, episode.alias,
            show.alias, ContentType='text/html; charset=utf-8')
    return html


def preview_episode(user, show, title, subtitle, description, audio_id,
                    image_id):
    episode = episode_operation.get_preview_episode(
        user, show, title, subtitle, description, audio_id, image_id)
    show_image = image_operation.get_image_or_assert(user, show.image_id) \
        if show.image_id else None
    return episode_html(user, show, show_image, episode)


def _delete_all_episodes(user, show):
    media_storage.delete_folder(settings.S3_BUCKET_SITES, show.alias)


def _get_site_url(show_alias):
    return '{}/{}'.format(settings.HOST_SITE, show_alias)
