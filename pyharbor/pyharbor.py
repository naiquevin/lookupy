import json


class Har(object):

    def __init__(self, filename):
        self.filename = filename
        self.har = read_har(filename)

    def entries(self, include=None, exclude=None, **kwargs):
        entries = filter_entries(get_entries(self.har), **kwargs)
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


def filter_entries(entries, pred=None, **kwargs):
    if pred is None:
        pred = lambda e: all(get_dunder_key(e, k) == v for k, v in kwargs.items())
    return (e for e in entries if pred(e))


def include_keys(entries, fields):
    return (dict((f, get_dunder_key(e, f)) for f in fields) for e in entries)


def exclude_keys(entries, fields):
    raise NotImplementedError


def get_dunder_key(_dict, key):
    parts = key.split('__', 1)
    try:
        result = _dict[parts[0]]
    except KeyError:
        return None
    else:
        return result if len(parts) == 1 else get_dunder_key(result, parts[1])


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
    # entries = filter_entries(get_entries(har), response__status=404)
    # print(list(include_keys(entries, ['request__url', 'response__status'])))
