Pyharbor
========

What and Why?
-------------

Pyharbor is a Python 3 library for working with HAR (HTTP Archive)
files. A considerably large HAR file is difficult to read and get an
insight out of. While there are existing solutions that can show a
chrome console like graph from the HAR, often we need a different
representation such as a comparative view of blocking timings of
assets w.r.t the domains etc. This lib simplifies this by providing a
django model layer like interface (think lookup fields such as
``store__user__username``) to extract only the required part of the
HAR for easy viewing and analysis.

It is still under development.


Requirements
------------

* Python >= 3.2
* nose (for running tests)


Why one more har file lib?
--------------------------

1. I wanted to extract data out of HAR files and none of the existing
   libs I found were well documented.
2. Really wanted to get started with Python 3.
3. For experimenting with stratified functional abstractions in Python.


Todo
----

* Nose tests
* Implement `exclude keys` function
* Allow querying request and response header list
* Implement CLI
* Document stuff

