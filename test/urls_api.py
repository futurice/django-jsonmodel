from __future__ import absolute_import
from django.conf.urls import include, url
from rest_framework import viewsets, routers

from test import viewsets

def register(router, name, viewset, **kw):
    router.register(name, viewset, base_name=name, **kw)

router = routers.DefaultRouter(trailing_slash=False)
register(router, r'person', viewsets.PersonViewSet)
register(router, r'account', viewsets.AccountViewSet)
register(router, r'computer', viewsets.ComputerViewSet)

urlpatterns = router.urls
