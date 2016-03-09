from django.core.urlresolvers import reverse
from djangojsonmodel.util import DotDict

import six

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

    Frontend handles filling in routing values.
    """
    for model, data in six.iteritems(c['models']):
        for field in data['fields']:
            u = DotDict()
            u.id = get_url('%s-detail'%(data['name'].lower()), args=[1]).replace('1', ':id')
            u.list = get_url('%s-list'%(data['name'].lower()))
            u.rel_id = get_url('%s-%s'%(data['name'], field['name']), args=[1,2]).replace('1', ':id').replace('2', ':relid')
            field['url'] = u
    return c
