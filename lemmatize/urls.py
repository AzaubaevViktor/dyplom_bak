from django.conf.urls import url, include

from . import views


api_urls = [
    url(r'search/(?P<name>[A-zА-я]+)/$', views.LemmaSearch.as_view()),
    url(r'processors$', views.ProcessorsView.as_view())
]


urlpatterns = [
    url(r'calc$', views.Calc.as_view()),
    url(r'index$', views.main),
    url(r'api/', include(api_urls)),
]