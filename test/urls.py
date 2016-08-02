from __future__ import absolute_import

from django.conf.urls import include, url

from test.views import index

urlpatterns = [
    url(r'^api/', include('test.urls_api')),
    url(r'^$', index, name="index")
]
