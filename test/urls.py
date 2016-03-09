from django.conf.urls import patterns, include, url

from django.conf.urls import patterns, include, url

from .views import index

urlpatterns = [
    url(r'^api/', include('test.urls_api')),
    url(r'^$', index, name="index")
]
