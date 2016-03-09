Django JSON Models [django-jsonmodels](https://github.com/futurice/django-jsonmodels) [![Build Status](https://travis-ci.org/futurice/django-jsonmodels.svg?branch=master)](https://travis-ci.org/futurice/django-jsonmodels)
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
```
