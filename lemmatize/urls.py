from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'graph$', views.graph),
    url(r'diff$', views.diff),
    url(r'diff2$', views.diff2),
    url(r'sliding$', views.sliding),
    url(r'max_list$', views.max_list)

]