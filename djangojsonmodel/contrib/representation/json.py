from __future__ import absolute_import
from django.core.serializers.json import DjangoJSONEncoder
import json, sys

def to_json(data, **kw):
    if sys.version_info.major < 3:
        kw['encoding'] = 'utf-8'
    return json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False, separators=(',',':'), **kw)
