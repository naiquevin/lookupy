from functools import partial


class Collection(object):

    def __init__(self, data):
        self.data = data

    @property
    def items(self):
        return QuerySet(self.data)

    def __iter__(self):
        for d in self.data:
            yield d


class QuerySet(object):

    def __init__(self, data):
        self.data = data

    def filter(self, *args, **kwargs):
        return QuerySet(filter_items(self.data, *args, **kwargs))

    def select(self, *args, **kwargs):
        flatten = kwargs.pop('flatten', False)
        f = flatten_keys if flatten else undunder_dict
        result = (f(d) for d in include_keys(self.data, args))
        return QuerySet(result)

    def __iter__(self):
        for d in self.data:
            yield d


## filter and lookup functions

def filter_items(items, *args, **kwargs):
    q1 = list(args) if args is not None else []
    q2 = [Q(**kwargs)] if kwargs is not None else []
    lookup_groups = q1 + q2
    pred = lambda item: all(lg.evaluate(item) for lg in lookup_groups)
    return (item for item in items if pred(item))


def lookup(key, val, item):
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

    def __init__(self):
        self.negate = False

    def evaluate(self, item):
        raise NotImplementedError


class LookupNode(LookupTreeElem):

    def __init__(self):
        super(LookupNode, self).__init__()
        self.children = []
        self.op = 'and'

    def add_child(self, child):
        self.children.append(child)

    def evaluate(self, item):
        results = map(lambda x: x.evaluate(item), self.children)
        result = any(results) if self.op == 'or' else all(results)
        return not result if self.negate else result

    def __invert__(self):
        newnode = LookupNode()
        newnode.negate = not self.negate
        return newnode


class LookupLeaf(LookupTreeElem):

    def __init__(self, **kwargs):
        super(LookupLeaf, self).__init__()
        self.lookups = kwargs

    def evaluate(self, item):
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


Q = LookupLeaf


## functions that work on the keys in a dict

def include_keys(items, fields):
    return (dict((f, dunder_key_val(item, f)) for f in fields) for item in items)


def dunder_key_val(_dict, key):
    parts = key.split('__', 1)
    try:
        result = _dict[parts[0]]
    except KeyError:
        return None
    else:
        return result if len(parts) == 1 else dunder_key_val(result, parts[1])


def undunder_key(key):
    return key.rsplit('__', 1)[-1]


def flatten_keys(_dict):
    keylist = list(_dict.keys())
    def decide_key(k, klist):
        newkey = undunder_key(k)
        return newkey if list(map(undunder_key, klist)).count(newkey) == 1 else k
    original_keys = [decide_key(key, keylist) for key in keylist]
    return dict(zip(original_keys, _dict.values()))


def undunder_dict(_dict):

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

