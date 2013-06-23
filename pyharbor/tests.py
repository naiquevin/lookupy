from nose.tools import assert_raises, assert_list_equal, assert_equal

from .pyharbor import dunder_key_val, get_entries, filter_items, \
    HarError, include_keys, original_keys, undunder_dict, Q


entries_fixtures = [{'request': {'url': 'http://example.com', 'headers': [{'name': 'Connection', 'value': 'Keep-Alive'}]},
                     'response': {'status': 404, 'headers': [{'name': 'Date', 'value': 'Thu, 13 Jun 2013 06:43:14 GMT'}]}},
                    {'request': {'url': 'http://example.org', 'headers': [{'name': 'Connection', 'value': 'Keep-Alive'}]},
                     'response': {'status': 200, 'headers': [{'name': 'Date', 'value': 'Thu, 13 Jun 2013 06:43:14 GMT'}]}},
                    {'request': {'url': 'http://example.com/myphoto.jpg', 'headers': [{'name': 'Connection', 'value': 'Keep-Alive'}]},
                     'response': {'status': 200, 'headers': [{'name': 'Date', 'value': 'Thu, 13 Jun 2013 06:43:14 GMT'}]}}]


def fe(entries, *args, **kwargs):
    return list(filter_items(entries, *args, **kwargs))


def ik(entries, fields):
    return list(include_keys(entries, fields))


## Tests

def test_get_key():
    d = dict([('a', 'A'),
              ('p', {'q': 'Q'}),
              ('x', {'y': {'z': 'Z'}})])
    assert dunder_key_val(d, 'a') == 'A'
    assert dunder_key_val(d, 'p__q') == 'Q'
    assert dunder_key_val(d, 'x__y__z') == 'Z'


def test_get_entries():
    d = {'log': {'entries': [{}, {}]}}
    assert len(get_entries(d)) == 2
    assert_raises(HarError, get_entries, {'log': {}})
    assert_raises(HarError, get_entries, {})


def test_Q():
    entries = entries_fixtures
    q1 = Q(response__status__exact=404, request__url__contains='.com')
    assert q1.evaluate(entries[0])

    # test with negation
    q2 = ~Q(response__status__exact=404)
    assert q2.evaluate(entries[1])
    # test multiple application of negation
    assert not (~q2).evaluate(entries[1])

    q3 = Q(response__status=200)
    assert not (q1 & q3).evaluate(entries[0])
    assert (q1 | q3).evaluate(entries[0])

    assert_list_equal(list(((Q(request__url__endswith='.jpg') | Q(response__status=404)).evaluate(e)
                      for e in entries)),
                      [True, False, True])

    assert_list_equal(list(((~Q(request__url__endswith='.jpg') | Q(response__status=404)).evaluate(e)
                      for e in entries)),
                      [True, True, False])


def test_filter_items():
    entries = entries_fixtures

    # when no lookup kwargs passed, all entries are returned
    assert_list_equal(fe(entries), entries)
    assert_list_equal(fe(entries, request__url='http://example.com'), entries[0:1])
    assert_list_equal(fe(entries, response__status=200), entries[1:])
    assert len(fe(entries, response__status=405)) == 0

    # testing individual types of lookups
    # exact
    assert len(fe(entries, request__url__exact='http://example.org')) == 1
    # neq
    assert len(fe(entries, request__url__neq='http://example.org')) == 2
    # (i)contains
    assert len(fe(entries, request__url__contains='example')) == 3
    assert len(fe(entries, request__url__icontains='ORG')) == 1
    # in
    assert len(fe(entries, response__status__in=[404, 200])) == 3
    assert len(fe(entries, response__status__in=[500, 503])) == 0
    assert len(fe(entries, response__status__in=[200])) == 2
    assert len(fe(entries, response__status__in=[])) == 0
    # (i)startswith
    assert len(fe(entries, request__url__startswith='https:')) == 0
    assert len(fe(entries, request__url__istartswith='HTTP:')) == 3
    # (i)endswith
    assert len(fe(entries, request__url__endswith='.jpg')) == 1
    assert len(fe(entries, request__url__iendswith='.JPG')) == 1
    # gt, gte
    assert len(fe(entries, response__status__gt=404)) == 0
    assert len(fe(entries, response__status__gte=404)) == 1
    # lt, lte
    assert len(fe(entries, response__status__lt=404)) == 2
    assert len(fe(entries, response__status__lte=404)) == 3

    # testing compund lookups
    assert len(fe(entries, Q(request__url__exact='http://example.org'))) == 1
    assert len(fe(entries, 
                  Q(request__url__exact='http://example.org', response__status=200)
                  |
                  Q(request__url__endswith='.com', response__status=404))) == 2

    assert len(fe(entries, 
                  ~Q(request__url__exact='http://example.org', response__status__gte=500)
                  |
                  Q(request__url__endswith='.com', response__status=404))) == 3

    assert len(fe(entries, 
                  ~Q(request__url__exact='http://example.org', response__status__gte=500)
                  |
                  Q(request__url__endswith='.com', response__status=404),
                  response__status__exact=200)) == 2


def test_include_keys():
    entries = entries_fixtures
    assert_list_equal(ik(entries, ['request']),
                      [{'request': {'url': 'http://example.com', 'headers': [{'name': 'Connection', 'value': 'Keep-Alive'}]}},
                       {'request': {'url': 'http://example.org', 'headers': [{'name': 'Connection', 'value': 'Keep-Alive'}]}},
                       {'request': {'url': 'http://example.com/myphoto.jpg', 'headers': [{'name': 'Connection', 'value': 'Keep-Alive'}]}}])

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


# check that response__status is flattened to 'status' since it's
# unique but 'response__headers' and 'request__headers' stay the same
# since, 'headers' is not unique
def test_original_keys():
    entry = {'request__url': 'http://example.com', 'request__headers': [{'name': 'Connection', 'value': 'Keep-Alive',}],
             'response__status': 404, 'response__headers': [{'name': 'Date', 'value': 'Thu, 13 Jun 2013 06:43:14 GMT'}]}
    assert_equal(original_keys(entry),
                 {'url': 'http://example.com',
                  'request__headers': [{'name': 'Connection', 'value': 'Keep-Alive',}],
                  'status': 404,
                  'response__headers': [{'name': 'Date', 'value': 'Thu, 13 Jun 2013 06:43:14 GMT'}]})


def test_undunder_dict():
    entry = {'request__url': 'http://example.com', 'request__headers': [{'name': 'Connection', 'value': 'Keep-Alive',}],
             'response__status': 404, 'response__headers': [{'name': 'Date', 'value': 'Thu, 13 Jun 2013 06:43:14 GMT'}]}
    assert_equal(undunder_dict(entry),
                 {'request': {'url': 'http://example.com', 'headers': [{'name': 'Connection', 'value': 'Keep-Alive',}]},
                  'response': {'status': 404, 'headers': [{'name': 'Date', 'value': 'Thu, 13 Jun 2013 06:43:14 GMT'}]}})
