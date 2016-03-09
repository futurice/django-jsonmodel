from django.test import TestCase

from djangojsonmodel.convert import jsmodels
from djangojsonmodel.contrib.human.mappings import shortnames

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
