import json


class Har(object):

    def __init__(self, filename):
        self.filename = filename
        self.har = read_har(filename)

    def entries(self, include=None, exclude=None, **kwargs):
        entries = filter_entries(self.har, **kwargs)
        if include is not None:
            return include_keys(entries, include)
        elif exclude is not None:
            return exclude_keys(entries, exclude)
        else:
            return entries


def read_har(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def filter_entries(har, **kwargs):
    pred = kwargs.pop('pred', None)
    if pred is None:
        pred = lambda e: all(get_key(e, k) == v for k, v in kwargs.items())
    return (e for e in har['log']['entries'] if pred(e))


def include_keys(entries, fields):
    return (dict((f, get_key(e, f)) for f in fields) for e in entries)


def exclude_keys(entries, fields):
    raise NotImplementedError


def get_key(_dict, key):
    parts = key.split('__', 1)
    try:
        result = _dict[parts[0]]
    except KeyError:
        return None
    else:
        return result if len(parts) == 1 else get_key(result, parts[1])


def test():
    d = dict([('a', 'A'),
              ('p', {'q': 'Q'}),
              ('x', {'y': {'z': 'Z'}})])
    assert get_key(d, 'a') == 'A'
    assert get_key(d, 'p__q') == 'Q'
    assert get_key(d, 'x__y__z') == 'Z'
    print('ok. All tests pass.')


if __name__ == '__main__':
    test()

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
    # entries = filter_entries(har, response__status=404)
    # print(list(include_keys(entries, ['request__url', 'response__status'])))

