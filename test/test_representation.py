from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from djangojsonmodel.convert import jsmodels
from djangojsonmodel.contrib.representation.json import to_json

class RepresentationTest(TestCase):
    def test_json(self):
        out = jsmodels(applications=['test',])
        self.assertTrue(to_json(out))
