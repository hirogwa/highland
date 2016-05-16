from flask import render_template
from highland import show_operation, episode_operation, media_storage


def update(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    episodes = episode_operation.load(user, show_id)
    html = render_template('public_sites/index.html',
                           show=show, episodes=episodes)
    # TODO key name
    media_storage.upload(html, str(show_id), 'show',
                         ContentType='text/html; charset=utf-8')
    return html


def update_episode(user, show_id, episode_id):
    show = show_operation.get_show_or_assert(user, show_id)
    episode = episode_operation.get_episode_or_assert(
        user, show_id, episode_id)
    html = render_template('public_sites/episode.html',
                           show=show, episode=episode)
    # TODO key name
    media_storage.upload(html, str(episode_id), 'episode',
                         ContentType='text/html; charset=utf-8')
    return html
