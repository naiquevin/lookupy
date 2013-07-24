"""

Examples showing how lookupy can be used with data obtained from the
Facebook graph API.

"""

import re
import os
import sys
import requests
from pprint import pprint

sys.path.append(os.path.abspath('../'))

from lookupy import Collection, Q

try:
    input = raw_input
except NameError:
    pass


FB_ID = None
FB_ACCESS_TOKEN = None


def fetch_posts(fb_id, access_token):
    url = 'https://graph.facebook.com/{fb_id}'.format(fb_id=fb_id)
    resp = requests.get(url, params={'fields': 'posts',
                                     'access_token': access_token})
    if resp.status_code == 200:
        return resp.json()['posts']
    else:
        raise Exception('Facebook API request failed with code: {status_code}'.format(status_code=resp.status_code))


if __name__ == '__main__':
    fb_id = input('Facebook ID: ') if FB_ID is None else FB_ID
    access_token = input('Facebook Access Token: ') if FB_ACCESS_TOKEN is None else FB_ACCESS_TOKEN

    posts = fetch_posts(fb_id, access_token)

    c = Collection(posts['data'])

    print("==== posts of type 'status' ====")
    statuses = c.filter(type__exact='status') \
                .select('message')
    pprint(list(statuses))
    print()

    print("==== posts of type 'links' ====")
    links = c.filter(type__exact='link') \
             .select('message')
    pprint(list(links))
    print()

    print("==== posts with at least 1 likes ====")
    liked = c.filter(likes__count__gte=1) \
             .select('message', 'likes')
    pprint(list(liked))
    print()

    print("==== posts about Erlang ====")
    about_erlang = c.filter(message__icontains='erlang') \
                    .select('message')
    pprint(list(about_erlang))
    print()

    print("==== posts created by the Twitter app ====")
    via_twitter = c.filter(application__name='Twitter') \
                   .select('message')
    pprint(list(via_twitter))
    print()

    print("=== posts having a hashtag or a mention ===")
    p1, p2 = map(re.compile, [r'@.+', r'#.+'])
    tags_mentions = c.filter(Q(message__regex=p1)
                             |
                             Q(message__regex=p2)) \
                     .select('message', 'from__name')
    pprint(list(tags_mentions))
    print()

