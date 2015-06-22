from django.conf.urls import url
from . import views


urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^problem_sets/$', views.problem_set_index, name='problem_set_index'),
  url(r'^problem_sets/(?P<ps_id>[0-9]+)/$', views.problem_set_detail, name='problem_set_detail'),
  url(r'^results/$', views.results_index, name='results_index'),
  url(r'^results/(?P<ps_id>[0-9]+)/$', views.results_detail, name='results_detail'),
]


