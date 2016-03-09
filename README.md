Django JSON Models [django-jsonmodel](https://github.com/futurice/django-jsonmodel) [![Build Status](https://travis-ci.org/futurice/django-jsonmodel.svg?branch=master)](https://travis-ci.org/futurice/django-jsonmodel)
==================

Convert Django Models into JSON representations.

Why?
----

Transform from the backend to the frontend without losing a beat.

Usage
-----

```
from djangojsonmodel.convert import jsmodels
jsmodels(applications=['contenttypes'])

{'models': {'ContentType': {'fields': [{'choices': OrderedDict(),
                                        'choices_ui': OrderedDict(),
                                        'default': None,
                                        'field': 'ManyToOneRel',
                                        'model': 'LogEntry',
                                        'name': 'logentry',
                                        'rel': {'child': 'LogEntry',
                                                'fk': False,
                                                'm2m': False,
                                                'reverse_fk': True},
                                        'required': True,
                                        'verbose_name': None},
                                        ...
```
