from django.core.urlresolvers import reverse
from djangojsonmodel.util import DotDict

def get_url(route, args=[], kwargs={}):
    try:
        return reverse(route, args=args, kwargs=kwargs)
    except Exception as e:
        return ''

def drf(c):
    """ Django Rest Framework
    url: POST
    url_id: PATCH
    lookup_url: Search (FK)
    """
    for model in c['models']:
        for field in c['models'][model]['fields']:
            # TODO: parent, child relationship
            u = DotDict()
            u.id = get_url('%s-%s'%(parent._meta.object_name, parent_name), args=[1]).replace('1', ':id')
            u.rel_id = get_url('%s-%s'%(parent._meta.object_name, child_name), args=[1,2]).replace('1', ':id').replace('2', ':relid')
            u.list = get_url('%s-list'%(rel_name_model))
            field['url'] = u
    return c
