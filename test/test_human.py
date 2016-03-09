from django.test import TestCase
from django.core.urlresolvers import reverse

from djangojsonmodel.convert import jsmodels
from djangojsonmodel.contrib.human.mappings import shortnames
from djangojsonmodel.contrib.human.urls import drf

from .urls import urlpatterns
from .urls_api import router

from pprint import pprint as pp

MAPPING = {
'BooleanField':'text',
'CharField':'text',
'DateTimeField':'datetime',
'DecimalField':'text',
'EmailField':'text',
'ForeignKey':'fk',
'ForeignObjectRel':'fk',
'IntegerField':'text',
'ManyToManyField':'m2m',
'TextField':'textarea',
'ChoiceField':'select',
}

def get_field(fields, name):
    return list(filter(lambda x: x['name']==name, fields))[0]

class HumanTest(TestCase):
    def test_human_shortnames(self):
        out = jsmodels(applications=['test',])
        out = shortnames(out, mapping=MAPPING)
        self.assertTrue(
                filter(lambda x: 'short_name' in x,
                    out['models']['Person']['fields']))
        for field in out['models']['Person']['fields']:
            if field['field'] == 'CharField':
                self.assertEquals(field['short_name'], 'text')

    def test_human_urls(self):
        self.assertTrue(reverse('person-list'))
        self.assertTrue(reverse('person-detail', kwargs=dict(pk=1)))

        out = jsmodels(applications=['test',], prepare=False)
        out = drf(out)

        f = get_field(out['models']['Account']['fields'], 'person')
        self.assertEqual(f['url']['id'], '/api/account/:id')
        f = get_field(out['models']['Account']['fields'], 'name')
        self.assertEqual(f['url']['id'], '/api/account/:id')

