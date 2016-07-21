import requests
import urllib.parse
from highland import settings, show_operation, episode_operation


def get_episode_by_day(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    p = {
        'bucket': settings.S3_BUCKET_AUDIO,
        'key_prefix': show.alias + '/'
    }
    r = requests.get(
        urllib.parse.urljoin(settings.HOST_OLYMPIA, '/stat/key_by_day'),
        params=p)
    return _convert_stat(user, show, r.json().get('keys'))


def get_episode_cumulative(user, show_id):
    show = show_operation.get_show_or_assert(user, show_id)
    p = {
        'bucket': settings.S3_BUCKET_AUDIO,
        'key_prefix': show.alias + '/'
    }
    r = requests.get(
        urllib.parse.urljoin(settings.HOST_OLYMPIA, '/stat/key_cumulative'),
        params=p)
    return _convert_stat(user, show, r.json().get('keys'))


def _convert_stat(user, show, stat):
    e_a_list = episode_operation.load_with_audio(user, show.id)
    key_to_episode = \
        {'{}/{}'.format(show.alias, a.guid): e for (e, a) in e_a_list}

    result = {}
    for k, v in [(k, v) for (k, v) in stat.items() if k in key_to_episode]:
        episode = key_to_episode.get(k)
        result[episode.id] = {
            'stat': v
        }
    return result
