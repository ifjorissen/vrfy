from django.conf.urls import url
from . import views


urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^(?P<ps_id>[0-9]+)/$', views.problem_set, name='problem_set_detail'),
]
