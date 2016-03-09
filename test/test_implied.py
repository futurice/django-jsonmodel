from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from djangojsonmodel.convert import jsmodels
from djangojsonmodel.contrib.db.rel import add_relations

from pprint import pprint as pp

class ImpliedTest(TestCase):
    def test_implied_content_type(self):
        implied = [{
            'model': ContentType,
            'field': 'content_type',
            'relname': 'contenttype',
            'verbose_name': 'Content Type',}]
        out = jsmodels(applications=['test',])
        out = add_relations(out, implied)
        self.assertTrue(
                filter(lambda x: x['name'] =='content_type',
                    out['models']['Person']['fields']))
        self.assertTrue(
                filter(lambda x: x['name'] =='content_type',
                    out['models']['Computer']['fields']))
