import requests
import urllib.parse
from highland import settings


def get_episode_by_day():
    p = {'bucket': settings.S3_BUCKET_AUDIO}
    r = requests.get(
        urllib.parse.urljoin(settings.HOST_OLYMPIA, '/stat/key_by_day'),
        params=p)
    return r.json().get('result')


def get_episode_cumulative():
    p = {'bucket': settings.S3_BUCKET_AUDIO}
    r = requests.get(
        urllib.parse.urljoin(settings.HOST_OLYMPIA, '/stat/key_cumulative'),
        params=p)
    return r.json().get('result')
