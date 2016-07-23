import datetime
import requests
import urllib.parse
from highland import settings, show_operation, episode_operation

DATE_FORMAT = '%Y%m%d'


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


def get_episode_one_week(user, show_id, date_to=None):
    if date_to:
        date_to = datetime.datetime.strptime(date_to, DATE_FORMAT)
    else:
        date_to = datetime.date.today()
    date_from = date_to - datetime.timedelta(days=6)

    return get_episode_cumulative(user, show_id,
                                  date_from.strftime(DATE_FORMAT),
                                  date_to.strftime(DATE_FORMAT))


def get_episode_cumulative(user, show_id, date_from=None, date_to=None):
    show = show_operation.get_show_or_assert(user, show_id)
    p = {
        'bucket': settings.S3_BUCKET_AUDIO,
        'key_prefix': show.alias + '/',
        'date_from': date_from,
        'date_to': date_to
    }
    r = requests.get(
        urllib.parse.urljoin(settings.HOST_OLYMPIA, '/stat/key_cumulative'),
        params=p)
    return _convert_stat(user, show, r.json().get('keys'), date_from, date_to)


def _convert_stat(user, show, key_stat, date_from=None, date_to=None):
    e_a_list = episode_operation.load_with_audio(user, show.id)
    key_to_episode = \
        {'{}/{}'.format(show.alias, a.guid): e for (e, a) in e_a_list}

    stat = {}
    for k, v in [(k, v) for (k, v) in key_stat.items() if k in key_to_episode]:
        episode = key_to_episode.get(k)
        stat[episode.id] = v
    return {
        'stat': stat,
        'date_from': date_from,
        'date_to': date_to
    }
