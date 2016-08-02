from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models
import django

from collections import OrderedDict
import json
import copy
import inspect
import logging

import six

from djangojsonmodel.db import m2m_relations, get_all_related_objects, get_field, is_reverse_fk
from djangojsonmodel.util import DotDict

logger = logging.getLogger(__name__)

def required(f, model):
    return (f.null is True) or (f.blank is True) or (f.default is not models.fields.NOT_PROVIDED)

def default(f, model):
    r = None
    if hasattr(f, 'default'):
        if callable(f.default):
            if inspect.isclass(f.default):
                pass
            else:
                r = f.default()
            if(isinstance(r, models.Model)):
                r = None
        else:
            r = f.default
    return r

def field_keys():
    return sorted(convert_field(ContentType._meta.get_fields()[0], ContentType).keys())

getrel = lambda relation: relation.remote_field if django.VERSION[:2] > (1, 8) else relation.related

def convert_field(f, model):
    m = DotDict()
    m.field = f.__class__.__name__
    m.model = get_field(f).model._meta.object_name
    m.name = f.name
    m.verbose_name = getattr(f, 'verbose_name', None)
    m.required = required(f, model)
    m.default = default(f, model)

    rel = DotDict()
    rel.m2m = isinstance(f, models.ManyToManyField)
    rel.reverse_fk = isinstance(f, models.ManyToOneRel) or isinstance(f, models.ManyToManyRel)
    rel.fk = isinstance(f, models.ForeignKey)
    rel.child = getrel(f).model._meta.object_name if getrel(f) else None
    m.rel = rel

    m.choices = OrderedDict(getattr(f, 'choices', {}))
    m.choices_ui = OrderedDict(getattr(f, 'choices_ui', {}))

    tmp = DotDict()
    tmp.field = f
    m.tmp = tmp

    return m

def create(applications=[]):
    result = DotDict()
    result.models = {}
    for model in apps.get_models():
        if model._meta.app_label not in applications:
            continue
        m = DotDict()
        m.name = model._meta.object_name
        m.fields = []

        tmp = DotDict()
        tmp.model = model
        m.tmp = tmp

        for field in model._meta.get_fields():
            jsfield = convert_field(field, model)
            m.fields.append(jsfield)
        result.models.setdefault(model._meta.object_name, {})
        result.models[model._meta.object_name] = m
    return result

def do_prepare(c):
    for model in c['models']:
        del c['models'][model]['tmp']
        for field in c['models'][model]['fields']:
            del field['tmp']
    return c

def jsmodels(applications=[], prepare=True):
    return do_prepare(create(applications)) if prepare else create(applications)

