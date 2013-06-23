import json


class Har(object):

    def __init__(self, filename):
        self.filename = filename
        self.har = read_har(filename)

    def entries(self, include=None, exclude=None, **kwargs):
        entries = filter_items(get_entries(self.har), **kwargs)
        if include is not None:
            return include_keys(entries, include)
        elif exclude is not None:
            return exclude_keys(entries, exclude)
        else:
            return entries


class HarError(Exception):
    pass


def read_har(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def get_entries(har):
    try:
        return har['log']['entries']
    except KeyError as e:
        raise HarError('Har file format invalid. Key {e} not found'.format(e=e))


def filter_items(items, *args, **kwargs):
    q1 = list(args) if args is not None else []
    q2 = [Q(**kwargs)] if kwargs is not None else []
    lookup_groups = q1 + q2
    pred = lambda item: all(lg.evaluate(item) for lg in lookup_groups)
    return (item for item in items if pred(item))


def include_keys(items, fields):
    return (dict((f, dunder_key_val(item, f)) for f in fields) for item in items)


def exclude_keys(items, fields):
    raise NotImplementedError


def lookup(key, val):
    init, last = key.rsplit('__', 1)
    dkv = dunder_key_val
    fin = false_if_none
    if last == 'exact':
        return lambda item: dkv(item, init) == val
    elif last == 'neq':
        return lambda item: dkv(item, init) != val
    elif last == 'contains':
        return lambda item: fin(dkv(item, init), lambda y: y.find(val) >= 0)
    elif last == 'icontains':
        return lambda item: fin(dkv(item, init), lambda y: y.lower().find(val.lower()) >= 0)
    elif last == 'in':
        return lambda item: dkv(item, init) in val
    elif last == 'startswith':
        return lambda item: fin(dkv(item, init), lambda y: y.startswith(val))
    elif last == 'istartswith':
        return lambda item: fin(dkv(item, init), lambda y: y.lower().startswith(val.lower()))
    elif last == 'endswith':
        return lambda item: fin(dkv(item, init), lambda y: y.endswith(val))
    elif last == 'iendswith':
        return lambda item: fin(dkv(item, init), lambda y: y.lower().endswith(val.lower()))
    elif last == 'gt':
        return lambda item: dkv(item, init) > val
    elif last == 'gte':
        return lambda item: dkv(item, init) >= val
    elif last == 'lt':
        return lambda item: dkv(item, init) < val
    elif last == 'lte':
        return lambda item: dkv(item, init) <= val
    else:
        return lambda item: dkv(item, key) == val


## Classes to compose compount lookups (Q object)

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
        result = all(lookup(k, v)(item) for k, v in self.lookups.items())
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


## some utility functions

def false_if_none(val, f):
    return False if val is None else f(val)


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


def original_keys(_dict):
    keylist = list(_dict.keys())
    def decide_key(k, klist):
        newkey = undunder_key(k)
        return newkey if list(map(undunder_key, klist)).count(newkey) == 1 else k
    original_keys = [decide_key(key, keylist) for key in keylist]
    return dict(zip(original_keys, _dict.values()))


def undunder_dict(_dict):

    def f(key, value, acc):
        parts = key.split('__')
        if len(parts) == 1:
            acc[parts[0]] = value
        else:
            acc[parts[0]] = f(parts[1], value, {})
        return acc

    result = {}
    for r in [f(k, v, {}) for k, v in _dict.items()]:
        rk = list(r.keys())[0]
        if rk not in result:
            result.update(r)
        else:
            result[rk].update(r[rk])
    return result


if __name__ == '__main__':
    pass
    # Usage:
    #
    # import sys
    #
    # script, filename = sys.argv
    #

    ## high level object oriented abstraction
    #
    # har = Har(filename)
    # entries = har.entries(response__status=404, include=['request__url', 'response__status'])
    # print(list(entries))
    #

    ## lower level functional abstraction
    #
    # har = read_har(filename)
    # entries = filter_items(get_entries(har), response__status=404)
    # print(list(include_keys(entries, ['request__url', 'response__status'])))
