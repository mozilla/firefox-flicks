import json

from nose.tools import eq_

from flicks.base.http import JSONResponse
from flicks.base.tests import TestCase


class JSONResponseTests(TestCase):
    def test_basic(self):
        response = JSONResponse({'blah': 'foo', 'bar': 7})
        eq_(json.loads(response.content), {'blah': 'foo', 'bar': 7})
        eq_(response.status_code, 200)

        response = JSONResponse(['baz', {'biff': False}])
        eq_(response.content, '["baz", {"biff": false}]')
        eq_(response.status_code, 200)

    def test_status(self):
        response = JSONResponse({'blah': 'foo', 'bar': 7}, status=404)
        eq_(json.loads(response.content), {'blah': 'foo', 'bar': 7})
        eq_(response.status_code, 404)
