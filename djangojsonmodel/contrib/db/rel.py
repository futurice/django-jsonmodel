
from djangojsonmodel.util import DotDict

def implied_relations(models):
    fields = []
    for k, model in enumerate(models):
        f = DotDict()
        f.required = False
        f.m2m = False
        f.reverse_fk = True
        f.child = model['relname']
        f.model = model['relname']
        f.name = model['field']
        f.verbose_name = model['verbose_name']
        f.type = 'fk'
        f.implied_relation = True
        fields.append(f)
    return fields

def add_relations(c, rels):
    for model in c['models']:
        c['models'][model]['fields'] += implied_relations(rels)
    return c
