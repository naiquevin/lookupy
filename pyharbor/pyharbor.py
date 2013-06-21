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


def filter_items(items, pred=None, **kwargs):
    if pred is None:
        pred = lambda e: all(lookup(e)(k)(v) for k, v in kwargs.items())
    return (e for e in items if pred(e))


def include_keys(items, fields):
    return (dict((f, dunder_key_val(item, f)) for f in fields) for item in items)


def exclude_keys(items, fields):
    raise NotImplementedError


def lookup(item):
    def curried(key):
        init, last = key.rsplit('__', 1)
        dkv = dunder_key_val
        fin = false_if_none
        if last == 'exact':
            return lambda x: dkv(item, init) == x
        elif last == 'neq':
            return lambda x: dkv(item, init) != x
        elif last == 'contains':
            return lambda x: fin(dkv(item, init), lambda y: y.find(x) >= 0)
        elif last == 'icontains':
            return lambda x: fin(dkv(item, init), lambda y: y.lower().find(x.lower()) >= 0)
        elif last == 'in':
            return lambda x: dkv(item, init) in x
        elif last == 'startswith':
            return lambda x: fin(dkv(item, init), lambda y: y.startswith(x))
        elif last == 'istartswith':
            return lambda x: fin(dkv(item, init), lambda y: y.lower().startswith(x.lower()))
        elif last == 'endswith':
            return lambda x: fin(dkv(item, init), lambda y: y.endswith(x))
        elif last == 'iendswith':
            return lambda x: fin(dkv(item, init), lambda y: y.lower().endswith(x.lower()))
        elif last == 'gt':
            return lambda x: dkv(item, init) > x
        elif last == 'gte':
            return lambda x: dkv(item, init) >= x
        elif last == 'lt':
            return lambda x: dkv(item, init) < x
        elif last == 'lte':
            return lambda x: dkv(item, init) <= x
        else:
            return lambda x: dkv(item, key) == x
    return curried


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
