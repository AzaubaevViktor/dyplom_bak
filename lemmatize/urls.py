from django.conf.urls import url, include
from rest_framework import routers

from . import views


api_urls = [
    url(r'search/(?P<name>[A-zА-я]+)/', views.LemmaSearch.as_view())
]

api_data_source = [
    url(r'source$', views.Source.as_view()),
    url(r'source_diff$', views.SourceDiff.as_view()),
    # url(r'diff$', views.diff),
    url(r'diff2$', views.diff2),
    url(r'sliding$', views.Sliding.as_view()),
    url(r'sliding_diff$', views.SlidingDiff.as_view()),
    url(r'sliding_diff_log$', views.SlidingDiffLog.as_view()),

]


urlpatterns = [
    url(r'data/', include(api_data_source)),
    url(r'index$', views.main),
    url(r'api/', include(api_urls)),
]