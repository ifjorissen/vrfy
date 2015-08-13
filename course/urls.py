from django.conf.urls import url
from . import views
# from . import receivers


urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^problem_sets/$', views.problem_set_index, name='problem_set_index'),

  #attempt & submit urls
  url(r'^attempt/problem-set(?P<ps_id>[0-9]+)/$', views.attempt_problem_set, name='attempt_problem_set'),
  url(r'^submit/problem-set(?P<ps_id>[0-9]+)/problem(?P<p_id>[0-9]+)/$', views.problem_submit, name='problem_submit'),
  url(r'^submit/success/problem-set(?P<ps_id>[0-9]+)/problem(?P<p_id>[0-9]+)/$', views.submit_success, name='submit_success'),

  #results urls
  url(r'^results/problem-set(?P<ps_id>[0-9]+)/problem(?P<p_id>[0-9]+)/$', views.results_problem_detail, name='results_problem_detail'),
  url(r'^results/problem-set(?P<ps_id>[0-9]+)/$', views.results_detail, name='results_detail'),
]


