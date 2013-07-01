Lookupy
=======

Lookupy is a Python library that provides a
[Django](http://djangoproject.com/)
[QuerySet](https://docs.djangoproject.com/en/1.5/ref/models/querysets/)
like interface to query (select and filter) data (list of
dictionaries). Needless to say, some ideas are shamelessly copied from
Django's core!

It actually started off as a library to parse and extract useful data
out of HAR (HTTP Archive) files but along the way I felt that a
generic library can be useful since I often find myself trying to get
data out of JSON collections.

Right now, it's still a WIP (but tests pass and it generally works).


Requirements
------------

* Python [tested in 2.7 and 3.2]
* [nose](http://pythontesting.net/framework/nose/nose-introduction/)
  [optional, for running tests]
* [coverage.py](http://nedbatchelder.com/code/coverage/)
  [optional, for measuring code test coverage]


Quick start
-----------

Since this library is based on Django QuerySets, it would help to
first understand how they work. In Django, QuerySets are used to
construct SQL queries to fetch data from the database e.g. using the
filter method of the QuerySet objects is equivalent to writing the
``WHERE`` clause in SQL.

Applying the same concept to simple collections of data (lists of
dicts), ``lookupy`` can be used to extract a subset of the data
depending upon some criteria. The criteria can be specified using
what is known as the "lookup parameters".

But first, we need to construct a ``Collection`` object out of the
data set as follows,

```python
    >>> from lookupy import Collection, Q

    >>> data = [{'framework': 'Django', 'language': 'Python', 'type': 'full-stack'},
    ...         {'framework': 'Flask', 'language': 'Python', 'type': 'micro'},
    ...         {'framework': 'Rails', 'language': 'Ruby', 'type': 'full-stack'},
    ...         {'framework': 'Sinatra', 'language': 'Ruby', 'type': 'micro'},
    ...         {'framework': 'Zend', 'language': 'PHP', 'type': 'full-stack'},
    ...         {'framework': 'Slim', 'language': 'PHP', 'type': 'micro'}]

    >>> c = Collection(data)
```

This collection exposes an attribute ``items`` which is a QuerySet.
Now to filter some data out of this, we call the ``filter`` method of
``items`` QuerySet passing our lookup parameters to it.

```python
    >>> c.items.filter(framework__startswith='S')
    <lookupy.lookupy.QuerySet object at 0xb740d40c>

    >>> list(c.items.filter(framework__startswith='S'))
    [{'framework': 'Sinatra', 'type': 'micro', 'language': 'Ruby'},
     {'framework': 'Slim', 'type': 'micro', 'language': 'PHP'}]
```

A lookup parameter is basically like a conditional clause and is of
the form ``<key>__<lookuptype>=<value>`` where ``<key>`` is a key in
the dict and ``<lookuptype>`` is one of the predefined keywords that
specify how to match the ``<value>`` with the actual value
corresponding to the key in each dict. See
[list of lookup types](#supported-lookup-types)

Multiple lookups are by default combined using the ``and`` logical
operator (``or`` and ``not`` are also supported as we will see in a
bit)

```python
    >>> list(c.items.filter(framework__startswith='S', language__exact='Ruby'))
    [{'framework': 'Sinatra', 'type': 'micro', 'language': 'Ruby'}]
```

For ``or`` and ``not``, we can compose a complex lookup using ``Q``
objects and pass them as positional arguments along with our lookup
parameters as keyword args. Not surprisingly, the bitwise and (``&``),
or (``|``) and inverse (``~``) are overriden to act as logical and, or
and not respectively (just the way it works in Django).

```python
    >>> list(c.items.filter(Q(language__exact='Python') | Q(language__exact='Ruby')))
    [{'framework': 'Django', 'language': 'Python', 'type': 'full-stack'},
     {'framework': 'Flask', 'language': 'Python', 'type': 'micro'},
     {'framework': 'Rails', 'language': 'Ruby', 'type': 'full-stack'},
     {'framework': 'Sinatra', 'language': 'Ruby', 'type': 'micro'}]

    >>> list(c.items.filter(~Q(language__startswith='R'), framework__endswith='go'))
    [{'framework': 'Django', 'language': 'Python', 'type': 'full-stack'}]
```

Lookupy also supports having the result contain only selected fields
by providing the ``select`` method on the QuerySet.

Calling the filter and select methods on a QuerySet returns another
QuerySet so these calls can be chained together. Internally, filtering
and selecting leverage Python's generators for lazy evaluation. Also,
``QuerySet`` and ``Collection`` both implement the
[iterator protocol](http://docs.python.org/2/tutorial/classes.html#iterators).

```python
    >>> result = c.items.filter(Q(language__exact='Python') | Q(language__exact='Ruby')) \
                        .filter(framework__istartswith='s')) \
                        .select('framework')

    >>> for item in result: # <-- this is where filtering will happen
    ...     print(item)
    ...
    [{'framework': 'Sinatra'}]
```

For nested dicts, the key in the lookup parameters can be constructed
using double underscores as ``request__status__exact=404``. Finally,
the data can also be filtered by nested collection of key-value pairs
using the same ``Q`` object.

```python
    >>> data = [{'a': 'python', 'b': {'p': 1, 'q': 2}, 'c': [{'name': 'version', 'value': '3.4'}, {'name': 'author', 'value': 'Guido van Rossum'}]},
    ...         {'a': 'erlang', 'b': {'p': 3, 'q': 4}, 'c': [{'name': 'version', 'value': 'R16B01'}, {'name': 'author', 'y': 'Joe Armstrong'}]}]
    >>> c = Collection(data)
    >>> list(c.items.filter(b__q__gte=4))
    [{'a': 'erlang', 'c': [{'name': 'version', 'value': 'R16B01'}, {'y': 'Joe Armstrong', 'name': 'author'}], 'b': {'q': 4, 'p': 3}}]
    >>> list(c.items.filter(c__filter=Q(name='version', value__contains='.')))
    [{'a': 'python', 'c': [{'name': 'version', 'value': '3.4'}, {'name': 'author', 'value': 'Guido van Rossum'}], 'b': {'q': 2, 'p': 1}}]
```

In the last example, we used the ``Q`` object to filter the original
dict by nested collection of key-value pairs i.e. we queried for only
those languages for which the version string contains a dot
(``.``). Note that this is different from filtering the nested
collections themselves. To do that, we can easily construct
``Collection`` objects for the child collections.


Supported lookup types
----------------------

These are the currently supported lookup types,

* ``exact`` exactly equality (default)
* ``neq`` inequality
* ``contains`` containment
* ``icontains`` insensitive containment
* ``in`` membership
* ``startswith`` string startswith
* ``istartswith`` insensitive startswith
* ``endswith`` string endswith
* ``iendswith`` insensitive endswith
* ``gt`` greater than
* ``gte`` greater than or equal to
* ``lt`` less than
* ``lte`` less than or equal to
* ``regex`` regular expression search
* ``filter`` nested filter


Todo
----

* Better test coverage
* Add examples
* Measure performance for larger data sets
* Implement CLI for JSON files
* Create package and upload to PyPI


License
-------

This library is provided as-is under the
[MIT License](http://opensource.org/licenses/MIT)

