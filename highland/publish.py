from highland import app, models, show_operation, public_view, \
    feed_operation, user_operation, image_operation, episode_operation


def publish_scheduled():
    episodes = episode_operation.load_publish_target()
    result = list()
    if not episodes:
        app.logger.info('no scheduled episode ready to publish found')
        return result

    def _reset(episode):
        user = user_operation.get_or_assert(episode.owner_user_id)
        show = show_operation.get(user.id, episode.show_id)
        show_image = image_operation.get_image_or_assert(user, show.image_id)
        return user, show, show_image, {
            'user_id': user.id,
            'show_id': show.id,
            'episode_ids': []
        }

    user, show, show_image, episode_summary = _reset(episodes[0])
    for episode in episodes:
        if episode.show_id != show.id:
            _update_show(user, show, show_image)
            result.appned(episode_summary)
            user, show, show_image, episode_summary = _reset(episode)
        episode_summary['episode_ids'].append(episode.id)
        public_view.episode_html(user, show, show_image, episode)
        episode_operation.publish(episode)
    _update_show(user, show, show_image)
    result.append(episode_summary)

    return result


def _update_show(user, show, show_image):
    public_view.show_html(user, show, show_image)
    feed_operation.update(user, show.id)
    app.logger.info('published show:{}'.format(show.id))


def publish(episode):
    '''Update public entity when an episode is updated
    '''
    if episode.draft_status != models.Episode.DraftStatus.published.name:
        app.logger.warning(
            'episode (user:{}, show:{}, id:{}) is not published. Ignoring.'.
            format(episode.owner_user_id, episode.show_id, episode.id))
        return

    user = user_operation.get_or_assert(episode.owner_user_id)
    show = show_operation.get(
        episode.owner_user_id, episode.show_id)
    show_image = image_operation.get_image_or_assert(user, show.image_id)
    public_view.episode_html(user, show, show_image, episode)
    public_view.show_html(user, show, show_image)
    feed_operation.update(user, show.id)
