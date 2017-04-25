from django.conf.urls import url

from timing import views

urlpatterns = [
    url(r'index$', views.main),
    url(r'data/simple$', views.times)
]