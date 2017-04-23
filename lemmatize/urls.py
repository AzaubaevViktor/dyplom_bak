from django.conf.urls import url, include
from rest_framework import routers

from . import views


api_urls = [
    url(r'search/(?P<name>[A-zА-я]+)/', views.LemmaSearch.as_view())
]

api_data_source = [
    url(r'source$', views.source),
    url(r'diff$', views.diff),
    url(r'diff2$', views.diff2),
    url(r'sliding$', views.sliding),
]


urlpatterns = [
    url(r'data/', include(api_data_source)),
    url(r'index$', views.main),
    url(r'api/', include(api_urls)),
]