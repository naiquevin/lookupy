"""
   lookupy.lookupy
   ~~~~~~~~~~~~~~~

   This module consists of all of the functionality of the package

"""

from functools import partial


class Collection(object):
    """Basic interface that provides QuerySet object from data

    It takes data as an iterable of dicts and provides a QuerySet
    instance that can be used for querying and filtering.

    Usually, you create a collection instance by passing the raw data
    and then access the ``items`` property of the collection object
    which would be a QuerySet::

        >>> import json
        >>> from lookupy.lookupy import Collection
        >>> with open('/path/to/data.json') as f:
        ...     data = json.load(f)
        ...     c = Collection(data)
        ...
        >>> c
        <lookupy.lookupy.Collection object at 0xb74a0c4c>
        >>> c.items
        <lookupy.lookupy.QuerySet object at 0xb74a0ccc>

    :param data: the data in form of an iterable of dictionaries

    """

    def __init__(self, data):
        self.data = data

    @property
    def items(self):
        return QuerySet(self.data)

    def __iter__(self):
        for d in self.data:
            yield d


class QuerySet(object):
    """Provides an interface to filter data and select specific fields
    from the data

    QuerySet is used for filtering data and also selecting only
    relevant fields out of it. This object is internally created which
    means usually you, the user wouldn't need to create it.

    :param data: an iterable of dicts

    """

    def __init__(self, data):
        self.data = data

    def filter(self, *args, **kwargs):
        """Filters data using the lookup parameters

        Lookup parameters can be passed as,

          1. keyword arguments of type `field__lookuptype=value` where
             lookuptype specifies how to "query" eg::

                 >>> c.items.filter(language__contains='java')

             above will match all items where the language field
             contains the substring 'java' such as 'java',
             'javascript'. Each look up is treated as a conditional
             clause and if multiple of them are passed, they are
             combined using logical the ``and`` operator

             For nested fields, double underscore can be used eg::

                 >>> data = [{'a': {'b': 3}}, {'a': {'b': 10}}]
                 >>> c = Collection(data)
                 >>> c.items.filter(a__b__gt=5)

             above lookup will match the 2nd element (b > 5)

             For the list of supported lookup parameter, see
             documentation on Github

          2. pos arguments of the type ``field__lookuptype=Q(...)``.
             These can be useful to build conditional clauses that
             need to be combined using logical `or` or negated using
             `not`

                 >>> c.items.filter(Q(language__exact='Python')
                                    |
                                    Q(language__exact='Ruby')

             above query will only filter the data where language is
             either 'Python' or 'Ruby'

        For more documentation see README on Github

        :param args   : ``Q`` objects
        :param kwargs : lookup parameters
        :rtype        : QuerySet

        """
        return QuerySet(filter_items(self.data, *args, **kwargs))

    def select(self, *args, **kwargs):
        """Selects specific fields of the data

        :param args   : field names to select
        :param kwargs : optional keyword args

        """
        flatten = kwargs.pop('flatten', False)
        f = flatten_keys if flatten else undunder_dict
        result = (f(d) for d in include_keys(self.data, args))
        return QuerySet(result)

    def __iter__(self):
        for d in self.data:
            yield d


## filter and lookup functions

def filter_items(items, *args, **kwargs):
    """Filters an iterable using lookup parameters

    :param items  : iterable
    :param args   : ``Q`` objects
    :param kwargs : lookup parameters
    :rtype        : lazy iterable (generator)

    """
    q1 = list(args) if args is not None else []
    q2 = [Q(**kwargs)] if kwargs is not None else []
    lookup_groups = q1 + q2
    pred = lambda item: all(lg.evaluate(item) for lg in lookup_groups)
    return (item for item in items if pred(item))


def lookup(key, val, item):
    """Checks if key-val pair exists in item using various lookup types

    :param key  : (str) that represents the field name to find
    :param val  : (mixed) object to match the value in the item against
    :param item : (dict)
    :rtype      : (boolean) True if field-val exists else False

    """
    parts = key.rsplit('__', 1)
    init, last = parts if len(parts) == 2 else (parts[0], None)
    dkv = dunder_key_val
    if last == 'exact':
        return dkv(item, init) == val
    elif last == 'neq':
        return dkv(item, init) != val
    elif last == 'contains':
        val = guard_str(val)
        return iff_not_none(dkv(item, init), lambda y: y.find(val) >= 0)
    elif last == 'icontains':
        val = guard_str(val)
        return iff_not_none(dkv(item, init), lambda y: y.lower().find(val.lower()) >= 0)
    elif last == 'in':
        val = guard_iter(val)
        return dkv(item, init) in val
    elif last == 'startswith':
        val = guard_str(val)
        return iff_not_none(dkv(item, init), lambda y: y.startswith(val))
    elif last == 'istartswith':
        val = guard_str(val)
        return iff_not_none(dkv(item, init), lambda y: y.lower().startswith(val.lower()))
    elif last == 'endswith':
        val = guard_str(val)
        return iff_not_none(dkv(item, init), lambda y: y.endswith(val))
    elif last == 'iendswith':
        val = guard_str(val)
        return iff_not_none(dkv(item, init), lambda y: y.lower().endswith(val.lower()))
    elif last == 'gt':
        return dkv(item, init) > val
    elif last == 'gte':
        return dkv(item, init) >= val
    elif last == 'lt':
        return dkv(item, init) < val
    elif last == 'lte':
        return dkv(item, init) <= val
    elif last == 'filter':
        val = guard_Q(val)
        result = guard_list(dkv(item, init))
        return len(list(filter_items(result, val))) > 0
    else:
        return dkv(item, key) == val


## Classes to compose compound lookups (Q object)

class LookupTreeElem(object):
    """Base class for a child in the lookup expression tree"""

    def __init__(self):
        self.negate = False

    def evaluate(self, item):
        raise NotImplementedError


class LookupNode(LookupTreeElem):
    """A node (element having children) in the lookup expression tree

    Typically it's any object composed of two ``Q`` objects eg::

        >>> Q(language__neq='Ruby') | Q(framework__startswith='S')
        >>> ~Q(language__exact='PHP')

    """

    def __init__(self):
        super(LookupNode, self).__init__()
        self.children = []
        self.op = 'and'

    def add_child(self, child):
        self.children.append(child)

    def evaluate(self, item):
        """Evaluates the expression represented by the object for the item

        :param item : (dict) item
        :rtype      : (boolean) whether lookup passed or failed

        """
        results = map(lambda x: x.evaluate(item), self.children)
        result = any(results) if self.op == 'or' else all(results)
        return not result if self.negate else result

    def __invert__(self):
        newnode = LookupNode()
        newnode.negate = not self.negate
        return newnode


class LookupLeaf(LookupTreeElem):
    """Class for a leaf in the lookup expression tree"""

    def __init__(self, **kwargs):
        super(LookupLeaf, self).__init__()
        self.lookups = kwargs

    def evaluate(self, item):
        """Evaluates the expression represented by the object for the item

        :param item : (dict) item
        :rtype      : (boolean) whether lookup passed or failed

        """
        result = all(lookup(k, v, item) for k, v in self.lookups.items())
        return not result if self.negate else result

    def __or__(self, other):
        node = LookupNode()
        node.op = 'or'
        node.add_child(self)
        node.add_child(other)
        return node

    def __and__(self, other):
        node = LookupNode()
        node.add_child(self)
        node.add_child(other)
        return node

    def __invert__(self):
        newleaf = LookupLeaf(**self.lookups)
        newleaf.negate = not self.negate
        return newleaf


# alias LookupLeaf to Q
Q = LookupLeaf


## functions that work on the keys in a dict

def include_keys(items, fields):
    """Function to keep only specified fields in data

    :param items  : iterable of dicts
    :param fields : (list) fieldnames to keep
    :rtype        : lazy iterable
    """
    return (dict((f, dunder_key_val(item, f)) for f in fields) for item in items)


def dunder_key_val(_dict, key):
    """Returns value for a specified "dunder_key"

    A dunder key is just a fieldname that may or may not contain
    double underscores (dunderscores!) for referrencing nested keys in
    a dict. eg::

         >>> data = {'a': {'b': 1}}
         >>> dunder_key_val(data, 'a__b')
         1

    key 'b' can be referrenced as 'a__b'

    :param _dict : (dict)
    :param key   : (str) that represents a first level or nested key in the dict
    :rtype       : (mixed) value corresponding to the key

    """
    parts = key.split('__', 1)
    try:
        result = _dict[parts[0]]
    except KeyError:
        return None
    else:
        return result if len(parts) == 1 else dunder_key_val(result, parts[1])


def undunder_key(key):
    """The final fieldname in a dunder key

    eg::

        >>> dunder_key('a__b__c')
        c

    :param key : (str) dunder key
    :rtype     : (str) last part of the dunder key
    """
    return key.rsplit('__', 1)[-1]


def flatten_keys(_dict):
    """Converts a nested dict to a flat one

    In doing so, it appends the nested keys as dunder keys to the dict
    eg::

        >>> flatten_keys({'a': 'hello', 'b': {'c': 'world'}})
        {'a': 'hello', 'b__c': 'world'}

    :param _dict : (dict) to flatten
    :rtype       : (dict) flattened result

    """
    keylist = list(_dict.keys())
    def decide_key(k, klist):
        newkey = undunder_key(k)
        return newkey if list(map(undunder_key, klist)).count(newkey) == 1 else k
    original_keys = [decide_key(key, keylist) for key in keylist]
    return dict(zip(original_keys, _dict.values()))


def undunder_dict(_dict):
    """Converts a flat dict with dunder keys to nested one

    eg::

        >>> undunder_dict({'a': 'hello', 'b__c': 'world'})
        {'a': 'hello', 'b': {'c': 'world'}}

    :param _dict : (dict) flat dict
    :rtype       : (dict) nested dict
    """

    def f(key, value, acc):
        parts = key.split('__')
        acc[parts[0]] = value if len(parts) == 1 else f(parts[1], value, {})
        return acc

    result = {}
    for r in [f(k, v, {}) for k, v in _dict.items()]:
        rk = list(r.keys())[0]
        if rk not in result:
            result.update(r)
        else:
            result[rk].update(r[rk])
    return result


## Exceptions

class LookupyError(Exception):
    pass


## utility functions

def iff(precond, val, f):
    return False if not precond(val) else f(val)

iff_not_none = partial(iff, lambda x: x is not None)


def guard_type(classinfo, val):
    if not isinstance(val, classinfo):
        raise LookupyError('Value not a {classinfo}'.format(classinfo=classinfo))
    return val

guard_str = partial(guard_type, str)
guard_list = partial(guard_type, list)
guard_Q = partial(guard_type, Q)

def guard_iter(val):
    try:
        iter(val)
    except TypeError:
        raise LookupyError('Value not an iterable')
    else:
        return val


if __name__ == '__main__':
    pass

