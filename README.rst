Lookupy
=======

What?
-----

Lookupy is a Python library that provides a Django QuerySet like
interface to query (select and filter) data (dicts and list of
dicts). Needless to say, some code and ideas are shamelessly copies
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

