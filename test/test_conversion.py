from __future__ import absolute_import
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory, TransactionTestCase
from django.test.client import Client
from django.utils.timezone import now

from .models import Person
from djangojsonmodel.convert import jsmodels
from pprint import pprint as pp

class ConversionTest(TestCase):
    def test_convert_contenttypes(self):
        out = jsmodels(applications=['contenttypes'])
        self.assertEquals(sorted(out['models'].keys()), ['ContentType'])
        self.assertEquals(
                list(filter(lambda x: x.get('name','')=='logentry',
                       out['models']['ContentType']['fields']))[0]['rel']['reverse_fk'],
                True)

    def test_convert_test(self):
        out = jsmodels(applications=['test',])
        self.assertEquals(sorted(out['models'].keys()), ['Account', 'Computer', 'Person'])
        self.assertEquals(
                sorted([k['name'] for k in out['models']['Person']['fields']]),
                ['account', 'age','computers','created','id','name'])
