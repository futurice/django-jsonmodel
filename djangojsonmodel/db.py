import django
from django.db import models

def m2m_relations(instance):
    return [f for f in instance._meta.get_fields() \
            if f.is_relation and f.many_to_many]

def get_all_related_objects(instance):
    return [f for f in instance._meta.get_fields()
        if (f.one_to_many or f.one_to_one) and f.auto_created]

def get_field(relation):
    if isinstance(relation, models.ManyToManyField):
        field = relation.remote_field if django.VERSION[:2] > (1, 8) else relation.related
    elif hasattr(relation, 'field'):
        field = relation.field
    else:
        field = relation
    return field

def is_reverse_fk(field, model):# 1:M
    f = get_field(field)
    return f and isinstance(f.model, model)
