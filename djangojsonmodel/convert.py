import django
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields.related import ForeignObjectRel
from django.template import Context, RequestContext, loader, Template
from django.template.loader import render_to_string
from django.apps import apps

from collections import OrderedDict

from decimal import Decimal
import datetime
import json
import copy
import inspect
import logging

import six

from djangojsonmodel.db import m2m_relations, get_all_related_objects, get_field, is_reverse_fk

logger = logging.getLogger(__name__)

class DotDictRaises(dict):
    __getattr__= dict.__getitem__
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

class TZAwareJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S%z")
        return super(TZAwareJSONEncoder, self).default(obj)

def to_json(data):
    return json.dumps(data, encoding='utf-8', cls=DjangoJSONEncoder, ensure_ascii=False, separators=(',',':'))

def get_url(route, args=[], kwargs={}):
    try:
        return reverse(route, args=args, kwargs=kwargs)
    except Exception as e:
        return ''

def implied_relations():
    phantom_models = [{'model': ContentType,
        'field': 'content_type',
        'relname': 'contenttype',
        'verbose_name': 'Content Type',}]
    fields = []
    for k, model in enumerate(phantom_models):
        f = DotDict()
        f.required = False
        rel_name = model['field']
        reverse_parent = model['model']
        rel_name_model = model['relname']
        f.m2m = False
        f.reverse_fk = True
        f.url = get_url('%s-%s'%(reverse_parent._meta.object_name, rel_name_model), args=[1]).replace('1', ':id')
        f.url_id = get_url('%s-%s'%(reverse_parent._meta.object_name, rel_name_model), args=[1,2]).replace('1', ':id').replace('2', ':relid')
        f.lookup_url = get_url('%s-list'%(rel_name_model))
        f.child = rel_name_model
        f.model = rel_name_model
        f.name = rel_name
        f.verbose_name = model['verbose_name']
        f.type = 'fk'
        fields.append(f)
    return fields

def handle(f, k):
    m = DotDict()

    m.required = True
    if (f.null is True) or (f.blank is True) or (f.default is not models.fields.NOT_PROVIDED):
        m.required = False

    m.default = None
    if hasattr(f, 'default'):
        if callable(f.default):
            if inspect.isclass(f.default):
                pass
            else:
                m.default = f.default()
            if(isinstance(m.default, models.Model)):
                logger.debug("NOTE: tried to use instance {} as default value, setting to None".format(type(m.default)))
                m.default = None
        else:
            m.default = f.default

    def reverse_fk(f, k, m):
        rel_name = f.rel.related_name or (f.opts.object_name)
        reverse_parent = f.related.parent_model
        parent_model = f.model
        rel_name_model = f.model._meta.object_name
        m.m2m = True
        m.reverse_fk = True
        m.url = get_url('%s-%s'%(reverse_parent._meta.object_name, rel_name_model), args=[1]).replace('1', ':id')
        m.url_id = get_url('%s-%s'%(reverse_parent._meta.object_name, rel_name_model), args=[1,2]).replace('1', ':id').replace('2', ':relid')
        m.lookup_url = get_url('%s-list'%(rel_name_model))
        m.child = rel_name_model
        m.model = rel_name_model
        if hasattr(parent_model, 'default_field'):
            m.dname = parent_model.default_field()
        m.name = rel_name
        m.verbose_name = f.model._meta.verbose_name
        
    if isinstance(f, models.ForeignKey):
        if is_reverse_fk(f, k):
            reverse_fk(f, k, m)
        else:
            parent_model = get_field(f).model
            rel_name = parent_model._meta.object_name
            m.fk = True
            m.lookup_url = get_url('%s-list'%(rel_name))
            m.child = rel_name
            m.model = rel_name
            if hasattr(parent_model, 'default_field'):
                m.dname = parent_model.default_field()
            m.name = f.name
            m.verbose_name = f.verbose_name
    elif isinstance(f, models.ManyToManyField):
        rel_name = get_field(f).model._meta.object_name
        m.m2m = True
        m.model = rel_name
        m.url = get_url('%s-%s-list'%(k._meta.object_name, rel_name), args=[1]).replace('1', ':id')
        m.url_id = get_url('%s-%s-detail'%(k._meta.object_name, rel_name), args=[1,2]).replace('1', ':id').replace('2', ':relid')
        m.lookup_url = get_url('%s-list'%(rel_name))
        m.required = False
        m.name = f.name
        m.verbose_name = f.verbose_name
    else:
        # non-relational fields
        m.verbose_name = getattr(f, 'verbose_name', None)
        m.name = f.name
    
    jtype = None
    for fk, fv in six.iteritems(FIELD_MAP):
        if is_reverse_fk(f, k):
            jtype = FIELD_MAP[ForeignObjectRel]
            break
        if isinstance(f, fk):
            jtype = fv
            break
    if jtype:
        m.type = jtype

    choices = getattr(f, 'choices', {})
    if choices:
        m.choices = OrderedDict(choices)
        m.type = 'select'
    choices_ui = getattr(f, 'choices_ui', {})

    if choices_ui:
        m.choices_ui = OrderedDict(choices_ui)
        m.type = 'select'

    return m

FIELD_MAP = {
models.CharField:'text',
models.DateTimeField:'datetime',
models.BooleanField:'text',
models.EmailField:'text',
models.TextField:'textarea',
models.IntegerField:'text',
ForeignObjectRel:'fk',
models.ForeignKey:'fk',
models.ManyToManyField:'m2m',
models.DecimalField:'text',
}

def create(applications=[], field_map={}):
    """
    url: POST
    url_id: PATCH
    lookup_url: Search (FK)
    """
    field_map = field_map or FIELD_MAP
    result = DotDict()
    result.models = {}
    for k in apps.get_models():
        if k._meta.app_label in applications:
            m = DotDict()
            m.url = None
            m.name = k._meta.object_name
            m.dname = 'name'
            if hasattr(k, 'default_field'):
                m.dname = k.default_field()
            m.fields = []
            m.url = get_url('%s-list'%(k._meta.object_name))
            m.url_id = get_url('%s-detail'%(k._meta.object_name), args=[1]).replace('1', ':id')
            # FIELDS+FOREIGNKEYS
            for f in k._meta.get_fields():
                jsfield = handle(f, k)
                if jsfield.get('type'):
                    m.fields.append(jsfield)
            # phantoms
            for imprel in implied_relations():
                m.fields.append(imprel)
            result.models.setdefault(k._meta.object_name, {})
            result.models[k._meta.object_name] = m
    return result

def jsmodels(applications=[], filename=None):
    rs = create(applications)

    if filename:
        formjs = to_json(rs);
        f = open(filename, 'w+')
        f.write("q.form = %s;" % (formjs))
        logger.debug("jsmodels(): {}".format(filename))

    return rs

