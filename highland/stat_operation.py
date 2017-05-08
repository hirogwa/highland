import requests
import urllib.parse
from datetime import date, datetime, timedelta
from highland import app, show_operation, episode_operation

DATE_FORMAT = '%Y%m%d'
STAT_USERS = 'users'
STAT_DOWNLOADS = 'downloads'


def get_episode_by_day(user, show_id, date_from=None, date_to=None):
    show = show_operation.get_model(show_id)
    p = {
        'bucket': app.config.get('S3_BUCKET_AUDIO'),
        'key_prefix': show.alias + '/'
    }
    if date_from:
        p['date_from'] = date_from
    if date_to:
        p['date_to'] = date_to

    r = requests.get(
        urllib.parse.urljoin(
            app.config.get('HOST_OLYMPIA'), '/stat/key_by_day'),
        params=p)
    episode_stat = _stat_from_audio_to_episode(
        user, show, r.json().get('keys'))
    stat, date_from, date_to = _fill_in_missing_date(
        episode_stat, date_from, date_to)
    return {
        'stat': stat,
        'date_from': date_from,
        'date_to': date_to
    }


def get_episode_one_week(user, show_id, date_to=None):
    if date_to:
        date_to = datetime.strptime(date_to, DATE_FORMAT)
    else:
        date_to = date.today()
    date_from = date_to - timedelta(days=6)

    return get_episode_cumulative(user, show_id,
                                  date_from.strftime(DATE_FORMAT),
                                  date_to.strftime(DATE_FORMAT))


def get_episode_cumulative(user, show_id, date_from=None, date_to=None):
    show = show_operation.get_model(show_id)
    p = {
        'bucket': app.config.get('S3_BUCKET_AUDIO'),
        'key_prefix': show.alias + '/',
        'date_from': date_from,
        'date_to': date_to
    }
    r = requests.get(
        urllib.parse.urljoin(
            app.config.get('HOST_OLYMPIA'), '/stat/key_cumulative'),
        params=p)
    return {
        'stat': _stat_from_audio_to_episode(user, show, r.json().get('keys')),
        'date_from': date_from,
        'date_to': date_to
    }


def _fill_in_missing_date(data, date_from, date_to):
    dates_from_data = [x for inner in data.values() for x in inner]
    date_from = date_from or min(dates_from_data)
    date_to = date_to or datetime.now().strftime(DATE_FORMAT)

    dt_from = datetime.strptime(date_from, DATE_FORMAT)
    dt_to = datetime.strptime(date_to, DATE_FORMAT)
    days = (dt_to - dt_from + timedelta(days=1)).days
    for d in [(dt_from + timedelta(days=x)).strftime(DATE_FORMAT)
              for x in range(days)]:
        for x in data.values():
            if d not in x:
                x[d] = {STAT_USERS: 0, STAT_DOWNLOADS: 0}

    return data, date_from, date_to


def _stat_from_audio_to_episode(user, show, key_stat):
    e_a_list = episode_operation.load_with_audio(show.id)
    key_to_episode = \
        {'{}/{}'.format(show.alias, a.guid): e for (e, a) in e_a_list}

    stat = {}
    for k, v in [(k, v) for (k, v) in key_stat.items() if k in key_to_episode]:
        episode = key_to_episode.get(k)
        stat[episode.id] = v
    return stat
