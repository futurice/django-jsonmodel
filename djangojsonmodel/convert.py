from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import get_app
from django.db.models.related import RelatedObject
from django.template import Context, RequestContext, loader, Template
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.core.serializers.json import DjangoJSONEncoder

from decimal import Decimal
import datetime
import json, copy
import inspect
import logging

log = logging.getLogger(__name__)

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
    except Exception, e:
        return ''

def is_reverse_fk(field, model):# 1:M
    return hasattr(field, 'related') and isinstance(field.related.parent_model(), model)

def implied_relations():
    phantom_models = [{'model': ContentType,
        'field': 'content_type',
        'relname': 'contenttype',
        'verbose_name': 'Content Type'}]
    fields = []
    for k, model in enumerate(phantom_models):
        f = DotDict()
        f.required = False
        rel_name = model['field']
        reverse_parent = model['model']
        rel_name_model = model['relname']
        f.m2m = False
        f.reverse_fk = True
        f.url = get_url('%s-%s'%(reverse_parent._meta.module_name, rel_name_model), args=[1]).replace('1', ':id')
        f.url_id = get_url('%s-%s'%(reverse_parent._meta.module_name, rel_name_model), args=[1,2]).replace('1', ':id').replace('2', ':relid')
        f.lookup_url = get_url('%s-list'%(rel_name_model))
        f.child = rel_name_model
        f.model = rel_name_model
        f.name = rel_name
        f.verbose_name = unicode(model['verbose_name'])
        f.type = 'marcopolo'
        fields.append(f)
    return fields

def handle(f, k):
    m = DotDict()

    m.required = True
    if (f.null is True) or (f.blank is True) or (f.default is not models.fields.NOT_PROVIDED):
        m.required = False

    if f.default:
        if callable(f.default):
            if inspect.isclass(f.default):
                pass
            else:
                m.default = f.default()
            if(isinstance(m.default, models.Model)):
                log.debug("NOTE: tried to use instance {} as default value, setting to None".format(type(m.default)))
                m.default = None
        else:
            m.default = f.default

    def reverse_fk(f, k, m):
        rel_name = f.rel.related_name or (f.opts.module_name)
        reverse_parent = f.related.parent_model
        parent_model = f.model
        rel_name_model = f.model._meta.module_name
        m.m2m = True
        m.reverse_fk = True
        m.url = get_url('%s-%s'%(reverse_parent._meta.module_name, rel_name_model), args=[1]).replace('1', ':id')
        m.url_id = get_url('%s-%s'%(reverse_parent._meta.module_name, rel_name_model), args=[1,2]).replace('1', ':id').replace('2', ':relid')
        m.lookup_url = get_url('%s-list'%(rel_name_model))
        m.child = rel_name_model
        m.model = rel_name_model
        if hasattr(parent_model, 'default_field'):
            m.dname = parent_model.default_field()
        m.name = rel_name
        m.verbose_name = unicode(f.model._meta.verbose_name)
        
    if isinstance(f, models.ForeignKey):
        if is_reverse_fk(f, k):
            reverse_fk(f, k, m)
        else:
            parent_model = f.related.parent_model
            rel_name = parent_model._meta.module_name
            m.fk = True
            m.lookup_url = get_url('%s-list'%(rel_name))
            m.child = rel_name
            m.model = rel_name
            if hasattr(parent_model, 'default_field'):
                m.dname = parent_model.default_field()
            m.name = f.name
            m.verbose_name = unicode(f.verbose_name)
    elif isinstance(f, models.ManyToManyField):
        rel_name = f.related.parent_model._meta.module_name
        m.m2m = True
        m.model = rel_name
        m.url = get_url('%s-%s-list'%(k._meta.module_name, rel_name), args=[1]).replace('1', ':id')
        m.url_id = get_url('%s-%s-detail'%(k._meta.module_name, rel_name), args=[1,2]).replace('1', ':id').replace('2', ':relid')
        m.lookup_url = get_url('%s-list'%(rel_name))
        m.required = False
        m.name = f.name
        m.verbose_name = unicode(f.verbose_name)
    else:
        # non-relational fields
        m.verbose_name = unicode(f.verbose_name)
        m.name = unicode(f.name)
    
    jtype = None
    for fk, fv in FIELD_MAP.iteritems():
        if is_reverse_fk(f, k):
            jtype = FIELD_MAP[models.related.RelatedObject]
            break
        if isinstance(f, fk):
            jtype = fv
            break
    if jtype:
        m.type = jtype

    choices = f.choices or getattr(f, 'choices_ui', None)
    if choices:
        m.choices = SortedDict(choices)
        m.type = 'select'

    return m

"""
Default mapping of model fields to JS widgets.
(27/1/2014) xeditable does not support bootstrap3 datetime
"""
FIELD_MAP = {
models.CharField:'text',
models.DateTimeField:'datetime',
models.BooleanField:'text',
models.EmailField:'text',
models.TextField:'textarea',
models.IntegerField:'text',
models.related.RelatedObject:'marcopolo',
models.ForeignKey:'select2',
models.ManyToManyField:'marcopolo',
models.DecimalField:'text',
}

def create(apps=[], field_map={}):
    """
    url: POST
    url_id: PATCH
    lookup_url: Search (FK)
    """
    field_map = field_map or FIELD_MAP
    result = DotDict()
    result.models = {}
    for k in models.get_models():
        if k._meta.app_label in apps:
            m = DotDict()
            m.url = None
            m.name = k._meta.module_name
            m.dname = 'name'
            if hasattr(k, 'default_field'):
                m.dname = k.default_field()
            m.fields = []
            m.url = get_url('%s-list'%(k._meta.module_name))
            m.url_id = get_url('%s-detail'%(k._meta.module_name), args=[1]).replace('1', ':id')
            # FIELDS+FOREIGNKEYS
            for f in k._meta.fields:
                jsfield = handle(f, k)
                if jsfield.get('type'):
                    m.fields.append(jsfield)
            # M2M
            for f in k._meta.get_m2m_with_model():
                jsfield = handle(f[0], k)
                if jsfield.get('type'):
                    m.fields.append(jsfield)
            # reverse relations
            for f in k._meta.get_all_related_objects():
                jsfield = handle(f.field, k)
                if jsfield.get('type'):
                    m.fields.append(jsfield)
            # phantoms
            for imprel in implied_relations():
                m.fields.append(imprel)
            result.models.setdefault(k._meta.module_name, {})
            result.models[k._meta.module_name] = m
    return result

tpls = {
    'xeditable': {'tpl': 'common/xeditable.html'},
    'xeditable_search': {'tpl': 'common/xeditable_search.html'},
}


def to_html(model, fields, extra={}, html=True):
    """ return HTML for model, for given fields """
    r = []
    include_fields_meta = {
        'source': {'quote': False},
        'api': {'quote': False},
    }
    include = []
    for k in model['fields']:
        name = k['name']
        row = {}
        if name in fields:
            name_extra = extra.get(name, {})
            tpl = name_extra.get('tpl', 'xeditable')
            c = dict(
                field=name,
                full=name,
                api=None,
                datatype=None,
                source=None,
            )
            c.update(name_extra)
            keys = c.keys()
            for key in keys:
                row[key] = c[key]
            row['tpl'] = tpls[tpl]['tpl']
            r.append(row)
    if html:
        out = []
        for k in r:
            data = "{{% xslot data='{0}' %}}".format(to_json(k))
            out.append(data)
        return "\n".join(out)
    return r

def to_html2(model):
    """ initial HTML for styling form pages """
    renderers = {
        'datetime': 'xeditable',
        'text': 'xeditable',
        'textarea': 'xeditable',
    }
    def get_tpl(name):
        if renderers.has_key(name):
            name = copy.deepcopy(renderers[name])
        return 'common/{0}.html'.format(name)
    html = []
    for k in model['fields']:
        row = render_to_string(get_tpl(k['type']), k)
        html.append(row)
    return "\n".join(html)

def jsmodels(apps=[], filename=None):
    rs = create(apps)

    if filename:
        formjs = to_json(rs);
        f = open(filename, 'w+')
        f.write("q.form = %s;" % (formjs))
        log.debug("jsmodels(): {}".format(filename))

    return rs

