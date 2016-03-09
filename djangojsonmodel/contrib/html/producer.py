from django.template import Context, RequestContext, loader, Template
from django.template.loader import render_to_string

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
