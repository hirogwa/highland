from flask import render_template
from highland import show_operation, episode_operation, media_storage, \
    settings, audio_operation


def update_full(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    episodes = episode_operation.load(user, show_id)
    _update_show(user, show, episodes)
    _delete_all_episodes(user, show)
    for episode in episodes:
        _update_episode(user, show, episode)
    return True


def _update_show(user, show, episodes, upload=True):
    html = render_template('public_sites/index.html',
                           show=show,
                           home_url='/{}'.format(show.alias),
                           episodes=episodes)
    if upload:
        media_storage.upload(html, settings.S3_BUCKET_SITES, show.alias,
                             ContentType='text/html; charset=utf-8')
    return html


def _update_episode(user, show, episode, upload=True):
    audio = audio_operation.get_audio_or_assert(user, episode.audio_id)
    html = render_template(
        'public_sites/episode.html',
        show=show,
        home_url='/{}'.format(show.alias),
        episode=episode,
        audio_url=audio_operation.get_audio_url(user, audio))
    if upload:
        media_storage.upload(
            html, settings.S3_BUCKET_SITES, episode.alias,
            show.alias, ContentType='text/html; charset=utf-8')
    return html


def _delete_all_episodes(user, show):
    media_storage.delete_folder(settings.S3_BUCKET_SITES, show.alias)
