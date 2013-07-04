import os
import json
from pprint import pprint
import operator
from functools import reduce

import sys

sys.path.append(os.path.abspath('../lookupy/'))

from lookupy import Collection, Q


f = open('www.youtube.com.har')
data = json.load(f)
f.close()

c = Collection(data['log']['entries'])

print("==== All javascript assets fetched ====")
js_assets = c.items.filter(response__content__mimeType='text/javascript') \
                   .select('request__url')
pprint(list(js_assets))
print()

print("==== URLs that were blocked ====")
blocked_urls = c.items.filter(timings__blocked__gt=0) \
                      .select('request__url')
pprint(list(blocked_urls))
print()

print("==== GET requests that responded with 200 OK ====")
get_200 = c.items.filter(request__method__exact='GET', 
                         response__status__exact=200) \
                 .select('request__url')
pprint(list(get_200))
print()

print("==== Requests that responded with status other than 200 ====")
not_200 = c.items.filter(response__status__neq=200).select('request__url')
pprint(list(not_200))
print()

print("==== Images ====")
images = c.items.filter(response__headers__filter=Q(name__exact='Content-Type', 
                                                    value__startswith='image/')) \
                .select('request__url', flatten=True)
pprint(list(images))
print()

print("==== Any of timings > 0 ===")
timings = ["blocked", "dns", "connect", "send", "wait", "receive", "ssl"]
timings_lookup = reduce(operator.or_, 
                        [Q(**{'timings__{t}__gt'.format(t=t): 0})
                         for t in timings])
pprint(list(c.items.filter(timings_lookup).select('request__url', 'timings')))
print()

