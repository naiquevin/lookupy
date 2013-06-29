Lookupy
=======

Lookupy is a Python library that provides a
[Django](http://djangoproject.com/)
[QuerySet](https://docs.djangoproject.com/en/1.5/ref/models/querysets/)
like interface to query (select and filter) data (list of
dicts). Needless to say, few bits of code and ideas are shamelessly
copied from Django's core!

It actually started off as a library to parse and extract useful data
out of HAR (HTTP Archive) files but along the way I felt that a
generic library can be useful since I often find myself trying to get
data out of json collections.

Rightnow, it's still a WIP (but tests pass and it generally works).


Requirements
------------

* Python >= 3.2
* [nose](http://pythontesting.net/framework/nose/nose-introduction/)
  [optional, for running tests]
* [coverage.py](http://nedbatchelder.com/code/coverage/)
  [optional to measure code test coverage]

Examples
--------

Here are some basic examples that show what this lib can do. More
coming soon, see ``lookupy.tests.py`` in the meanwhile :-)

```python

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
```


Why Python3?
------------

I wanted to use it as an opportunity to (finally) get started with
Python 3. Eventually I will make sure that it works with Python 2 as
well since that's what I mostly use at other times.


Todo
----

* Document stuff
* Better test coverage
* Implement CLI for json files


LICENSE
-------

[MIT License](http://opensource.org/licenses/MIT)

