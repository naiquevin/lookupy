import os
import sys

sys.path.append(os.path.abspath('../lookupy/'))

from lookupy import Collection, Q

data = [{'framework': 'Django', 'language': 'Python', 'type': 'full-stack'},
        {'framework': 'Flask', 'language': 'Python', 'type': 'micro'},
        {'framework': 'Rails', 'language': 'Ruby', 'type': 'full-stack'},
        {'framework': 'Sinatra', 'language': 'Ruby', 'type': 'micro'},
        {'framework': 'Zend', 'language': 'PHP', 'type': 'full-stack'},
        {'framework': 'Slim', 'language': 'PHP', 'type': 'micro'}]

print('Data is a list of dict')
print(data)
print()

c = Collection(data)

print('Collection wraps data')
print(c)
print()

print('Collection provides QuerySet as it\'s ``items`` attribute')
print(c.items)
print()

print('filter returns a lazy QuerySet')
print(c.items.filter(framework__startswith='S'))
print()

print('items in which the framework field startswith \'S\'')
print(list(c.items.filter(framework__startswith='S')))
print()

print('items in which the framework field startswith \'S\' and language is \'Ruby\'')
print(list(c.items.filter(framework__startswith='S', language__exact='Ruby')))
print()

print('items in which language is \'Python\' *or* \'Ruby\' ')
print(list(c.items.filter(Q(language__exact='Python') | Q(language__exact='Ruby'))))
print()

print('items in which language is \'Python\' *or* \'Ruby\' *and* framework name startswith \'s\' and selected to show only the \'framework field\'')
result = c.items.filter(Q(language__exact='Python') | Q(language__exact='Ruby')) \
                .filter(framework__istartswith='s') \
                .select('framework')
print(list(result))
print()

