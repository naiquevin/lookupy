Lookupy
=======

Lookupy is a Python library that provides a Django QuerySet like
interface to query (select and filter) data (dicts and list of
dicts). Needless to say, some code and ideas are shamelessly copied
from Django's core.

It actually started off as a library to parse and extract useful data
out of HAR (HTTP Archive) files but along the way I felt that a
generic library can be useful since I often find myself trying to get
data out of json collections.

It is still pretty much under development.


Requirements
------------

* Python >= 3.2
* nose (for running tests)


Examples
--------

Here are some basic examples, see ``lookupy.tests.py`` for more of them::

    from lookupy.lookupy import Collection, Q

    data = [{'framework': 'Django', 'language': 'Python', 'type': 'full-stack'},
            {'framework': 'Flask', 'language': 'Python', 'type': 'micro'},
            {'framework': 'Rails', 'language': 'Ruby', 'type': 'full-stack'},
            {'framework': 'Sinatra', 'language': 'Ruby', 'type': 'micro'},
            {'framework': 'Zend', 'language': 'PHP', 'type': 'full-stack'},
            {'framework': 'Slim', 'language': 'PHP', 'type': 'micro'}]

    c = Collection(data)
    c.items.filter(framework__startswith='S')
    # <lookupy.lookupy.QuerySet object at 0xb740d40c>

    list(c.items.filter(framework__startswith='S'))
    # [{'framework': 'Sinatra', 'type': 'micro', 'language': 'Ruby'},
    #  {'framework': 'Slim', 'type': 'micro', 'language': 'PHP'}]

    list(c.items.filter(Q(language__exact='Python') | Q(language__exact='Ruby'))\
                .select('framework'))
    # [{'framework': 'Django'},
    #  {'framework': 'Flask'},
    #  {'framework': 'Rails'},
    #  {'framework': 'Sinatra'}]

    list(c.items.filter(Q(language__exact='Python') | Q(language__exact='Ruby'))\
                .filter(framework__istartswith='s'))
    # [{'framework': 'Sinatra', 'type': 'micro', 'language': 'Ruby'}]


Why Python3?
------------

I really wanted to get started with Python 3. Eventually I will make
sure that it works with Python 2 as well as that's what I mostly use
at other times.


Todo
----

* Document stuff
* Better test coverage
* Implement CLI for json files

