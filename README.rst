Lookupy
=======

Lookupy is a Python library that provides a `Django
<http://djangoproject.com/>`_ `QuerySet
<https://docs.djangoproject.com/en/1.5/ref/models/querysets/>`_ like
interface to query (filter and select) data (list of dictionaries).

It actually started off as a library to parse and extract useful data
out of HAR (HTTP Archive) files but along the way I felt that a
generic library can be useful since I often find myself trying to get
data out of JSON collections such as those obtained from facebook or
github APIs. I choose to imitate the Django queryset API because of my
familiarity with it.

I don't use this library all the time but I do find it helpful when
working with deeply nested json/dicts - the kind that Facebook, Github
etc. APIs return. For everyday stuff I prefer Python's built-in
functional constructs such as map, filter, list comprehensions.

Requirements
------------

* Python [tested for 2.7 and 3.2]
* `nose <http://pythontesting.net/framework/nose/nose-introduction/>`_
  [optional, for running tests]
* `coverage.py <http://nedbatchelder.com/code/coverage/>`_
  [optional, for test coverage]
* `Tox <https://pypi.python.org/pypi/tox>`_
  [optional, for building and testing on different versions of Python]


Installation
------------

This package is not yet uploaded to PyPI which I plan to do once I
have tested it enough. So for now it can be installed from github via
pip as follows.

.. code-block:: bash
    
    $ pip install git+git://github.com/naiquevin/lookupy.git

**Tip!** Consider installing inside a
  `virtualenv <http://www.virtualenv.org/en/release-1.10/>`_


Quick start
-----------

Since this library is based on Django QuerySets, it would help to
first understand how they work. In Django, QuerySets are used to
construct SQL queries to fetch data from the database. Using the
filter method of the QuerySet objects is equivalent to writing the
*WHERE* clause in SQL.

Applying the same concept to simple collections of data (lists of
dicts), lookupy can be used to extract a subset of the data depending
upon some criteria that is specified using what is known as the
"lookup parameters".

But first, we need to construct a *Collection* object out of the
data set as follows,

.. code-block:: pycon

    >>> from lookupy import Collection, Q
    >>> data = [{'framework': 'Django', 'language': 'Python', 'type': 'full-stack'},
    ...         {'framework': 'Flask', 'language': 'Python', 'type': 'micro'},
    ...         {'framework': 'Rails', 'language': 'Ruby', 'type': 'full-stack'},
    ...         {'framework': 'Sinatra', 'language': 'Ruby', 'type': 'micro'},
    ...         {'framework': 'Zend', 'language': 'PHP', 'type': 'full-stack'},
    ...         {'framework': 'Slim', 'language': 'PHP', 'type': 'micro'}]
    >>> c = Collection(data)

In order to filter some data out of collection, we call the *filter*
method passing our lookup parameters to it.

.. code-block:: pycon

    >>> c.filter(framework__startswith='S')
    <lookupy.lookupy.QuerySet object at 0xb740d40c>

    >>> list(c.filter(framework__startswith='S'))
    [{'framework': 'Sinatra', 'type': 'micro', 'language': 'Ruby'},
    {'framework': 'Slim', 'type': 'micro', 'language': 'PHP'}]


A lookup parameter is basically like a conditional clause and is of
the form *<key>__<lookuptype>=<value>* where *<key>* is a key in the
dict and *<lookuptype>* is one of the predefined keywords that specify
how to match the *<value>* with the actual value corresponding to the
key in each dict. See `list of lookup types
<#supported-lookup-types>`_

Multiple lookups passed as args are by default combined using the
*and* logical operator (*or* and *not* are also supported as we will
see in a bit)

.. code-block:: pycon

    >>> list(c.filter(framework__startswith='S', language__exact='Ruby'))
    [{'framework': 'Sinatra', 'type': 'micro', 'language': 'Ruby'}]


For *or* and *not*, we can compose a complex lookup using *Q* objects
and pass them as positional arguments along with our lookup parameters
as keyword args. Not surprisingly, the bitwise and (*&*), or (*|*) and
inverse (*~*) are overriden to act as logical *and*, *or* and *not*
respectively (just the way it works in Django).

.. code-block:: pycon

    >>> list(c.filter(Q(language__exact='Python') | Q(language__exact='Ruby')))
    [{'framework': 'Django', 'language': 'Python', 'type': 'full-stack'},
     {'framework': 'Flask', 'language': 'Python', 'type': 'micro'},
     {'framework': 'Rails', 'language': 'Ruby', 'type': 'full-stack'},
     {'framework': 'Sinatra', 'language': 'Ruby', 'type': 'micro'}]
    >>> list(c.filter(~Q(language__startswith='R'), framework__endswith='go'))
    [{'framework': 'Django', 'language': 'Python', 'type': 'full-stack'}]

Lookupy also supports having the result contain only selected fields
by providing the *select* method on the QuerySet objects.

Calling the filter or select methods on a QuerySet returns another
QuerySet so these calls can be chained together. Internally, filtering
and selecting leverage Python's generators for lazy evaluation. Also,
*QuerySet* and *Collection* both implement the `iterator protocol
<http://docs.python.org/2/tutorial/classes.html#iterators>`_ so
nothing is evaluated until consumption.

.. code-block:: pycon

    >>> result = c.filter(Q(language__exact='Python') | Q(language__exact='Ruby')) \
                        .filter(framework__istartswith='s')) \
                        .select('framework')
    >>> for item in result: # <-- this is where filtering will happen
    ...     print(item)
    ...
    [{'framework': 'Sinatra'}]

For nested dicts, the key in the lookup parameters can be constructed
using double underscores as *request__status__exact=404*. Finally,
data can also be filtered by nested collection of key-value pairs
using the same *Q* object.

.. code-block:: pycon

    >>> data = [{'a': 'python', 'b': {'p': 1, 'q': 2}, 'c': [{'name': 'version', 'value': '3.4'}, {'name': 'author', 'value': 'Guido van Rossum'}]},
    ...         {'a': 'erlang', 'b': {'p': 3, 'q': 4}, 'c': [{'name': 'version', 'value': 'R16B01'}, {'name': 'author', 'y': 'Joe Armstrong'}]}]
    >>> c = Collection(data)
    >>> list(c.filter(b__q__gte=4))
    [{'a': 'erlang', 'c': [{'name': 'version', 'value': 'R16B01'}, {'y': 'Joe Armstrong', 'name': 'author'}], 'b': {'q': 4, 'p': 3}}]
    >>> list(c.filter(c__filter=Q(name='version', value__contains='.')))
    [{'a': 'python', 'c': [{'name': 'version', 'value': '3.4'}, {'name': 'author', 'value': 'Guido van Rossum'}], 'b': {'q': 2, 'p': 1}}]

In the last example, we used the *Q* object to filter the original
dict by nested collection of key-value pairs i.e. we queried for only
those languages for which the version string contains a dot
(*.*). Note that this is different from filtering the nested
collections themselves. To do that, we can easily construct
*Collection* objects for the child collections.

See the *examples* subdirectory for more usage examples.


Supported lookup types
----------------------

These are the currently supported lookup types,

* **exact** exact equality (default)
* **neq** inequality
* **contains** containment
* **icontains** insensitive containment
* **in** membership
* **startswith** string startswith
* **istartswith** insensitive startswith
* **endswith** string endswith
* **iendswith** insensitive endswith
* **gt** greater than
* **gte** greater than or equal to
* **lt** less than
* **lte** less than or equal to
* **regex** regular expression search
* **filter** nested filter


Gotchas!
--------

1. If a non-existent *key* is passed to *select*, then it will be
   included in the result with value *None* for all results.

2. If a non-existent *key* is passed to *filter*, then the lookup will
   always fail. At first, this doesn't seem consistent with the first
   point but it's done to keep the overall behaviour predictable
   e.g. If a non-existent key is used with *lt* lookup with integer,
   say *2*, as the val, then the lookup will always fail even though
   *None < 2 == True* in Python 2. Best is to just avoid such
   situations.

3. Because of the way *select* works at the moment, if chained with
   *filter* it should be called only after it and not before (unless the
   keys used for lookup are also being selected.) I plan to fix this in
   later releases.


Running tests
-------------

.. code-block:: bash

    $ make test


Todo
----

* Measure performance for larger data sets
* Implement CLI for JSON files
* Create package and upload to PyPI


License
-------

This library is provided as-is under the
`MIT License <http://opensource.org/licenses/MIT>`_
