## This module deals with code that deals with handling the nested
## dict functionality

def make_neskey(*args):
    """Produces a nested key from multiple args separated by double
    underscore
    
       >>> make_neskey('a', 'b', 'c')
       >>> 'a__b__c'

    :param *args : *String
    :rtype       : String
    """
    return '__'.join(args)


def neskey_split(neskey):
    """Splits a neskey into 2 parts

    The first part is everything before the final double underscore
    The second part is after the final double underscore

        >>> neskey_split('a__b__c')
        >>> ('a__b', 'c')

    :param neskey : String
    :rtype        : 2 Tuple
    """
    parts = neskey.rsplit('__', 1)
    return tuple(parts) if len(parts) > 1 else (parts[0], None)


def neskey_init(neskey):
    """Returns the initial part of the nested key

        >>> neskey_init('a__b__c')
        >>> 'a__b'

    :param neskey : String
    :rtype        : String
    """
    return neskey_split(neskey)[0]


def neskey_last(neskey):
    """Returns the last part of the nested key

        >>> neskey_last('a__b__c')
        >>> 'c'
    
    :param neskey : String
    :rtype        : String
    """
    return neskey_split(neskey)[1]


def nesget(_dict, key):
    """Returns value for a specified "neskey"

    A "neskey" is just a fieldname that may or may not contain double
    underscores (dunderscores!) for referrencing nested keys in a
    dict. eg::

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
        return result if len(parts) == 1 else nesget(result, parts[1])


def flat_to_nested(_dict):
    """Converts a flat dict with "neskeys" to nested one

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


def nested_to_flat(_dict):
    """Converts a nested dict to a flat one

    In doing so, it appends the nested keys as dunder keys to the dict
    eg::

        >>> flatten_keys({'a': 'hello', 'b': {'c': 'world'}})
        {'a': 'hello', 'c': 'world'}
        >>> flatten_keys({'a': {'p': 'yay'}, 'b': {'p': 'no'}})
        {'a__p': 'yay', 'b__p': 'no'}

    :param _dict : (dict) to flatten
    :rtype       : (dict) flattened result

    """
    keylist = list(_dict.keys())
    def decide_key(k, klist):
        newkey = neskey_last(k)
        return newkey if list(map(neskey_last, klist)).count(newkey) == 1 else k
    original_keys = [decide_key(key, keylist) for key in keylist]
    return dict(zip(original_keys, _dict.values()))

