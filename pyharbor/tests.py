from nose.tools import assert_raises, assert_list_equal

from .pyharbor import get_key, get_entries, filter_entries, \
    HarError, include_keys


entries_fixtures = [{'request': {'url': 'http://example.com'}, 'response': {'status': 404}},
                    {'request': {'url': 'http://example.org'}, 'response': {'status': 200}},
                    {'request': {'url': 'http://myphoto.jpg'}, 'response': {'status': 200}}]


def test_get_key():
    d = dict([('a', 'A'),
              ('p', {'q': 'Q'}),
              ('x', {'y': {'z': 'Z'}})])
    assert get_key(d, 'a') == 'A'
    assert get_key(d, 'p__q') == 'Q'
    assert get_key(d, 'x__y__z') == 'Z'


def test_get_entries():
    d = {'log': {'entries': [{}, {}]}}
    assert len(get_entries(d)) == 2
    assert_raises(HarError, get_entries, {'log': {}})
    assert_raises(HarError, get_entries, {})


def test_filter_entries():
    entries = entries_fixtures

    def fe(entries, pred=None, **kwargs):
        return list(filter_entries(entries, pred, **kwargs))

    # when no lookup kwargs passed, all entries are returned
    assert_list_equal(fe(entries), entries)
    assert_list_equal(fe(entries, request__url='http://example.com'), entries[0:1])
    assert_list_equal(fe(entries, response__status=200), entries[1:])
    assert len(fe(entries, response__status=405)) == 0

    # test with non None pred
    dotorgs = fe(entries, pred=lambda x: x['request']['url'].endswith('.org'))
    assert_list_equal(dotorgs, entries[1:2])

    # test that pred takes preferrence if both pred and lookup kwargs passed
    images = fe(entries,
                pred=lambda x: x['request']['url'].endswith('.jpg'),
                response__status=302)
    assert_list_equal(images, entries[2:3])


def test_include_keys():
    entries = entries_fixtures

    def ik(entries, fields):
        return list(include_keys(entries, fields))

    assert_list_equal(ik(entries, ['request']),
                      [{'request': {'url': 'http://example.com'}},
                       {'request': {'url': 'http://example.org'}},
                       {'request': {'url': 'http://myphoto.jpg'}}])


    assert_list_equal(ik(entries, ['response__status']),
                      [{'response__status': 404},
                       {'response__status': 200},
                       {'response__status': 200}])

    # when an empty list is passed as fields
    assert_list_equal(ik(entries, []), [{},{},{}])

    # when a non-existent key is passed in fields
    assert_list_equal(ik(entries, ['response__status', 'cookies']),
                      [{'response__status': 404, 'cookies': None},
                       {'response__status': 200, 'cookies': None},
                       {'response__status': 200, 'cookies': None}])
