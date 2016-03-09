from django.db import models
from django.db.models.fields.related import ForeignObjectRel

from djangojsonmodel.util import DotDict

import six

def sname(field, model, mapping):
    n = mapping.get(field['field'], None)
    if field['choices'] or field['choices_ui']:
        n = mapping.get('ChoiceField')
    return n

def shortnames(c, mapping):
    for model in c['models']:
        for field in c['models'][model]['fields']:
            field['short_name'] = sname(field, model, mapping)
    return c
