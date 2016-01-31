from django.conf.urls import url
from . import views
from django.views.generic import TemplateView
# from . import receivers

app_name="course"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^logged_out/$', views.logout_view, name='logged_out'),
    url(r'^problem_sets/$', views.problem_set_index, name='problem_set_index'),
    url(r'^your_solutions/$', views.your_solutions, name='your_solutions'),
    # attempt & submit urls
    url(r'^attempt/problem-set(?P<ps_id>[0-9]+)/$',
        views.attempt_problem_set,
        name='attempt_problem_set'),
    url(
        r'^submit/problem-set(?P<ps_id>[0-9]+)/problem(?P<p_id>[0-9]+)/$',
        views.problem_submit,
        name='problem_submit'),
    url(
        r'^submit/success/problem-set(?P<ps_id>[0-9]+)/problem(?P<p_id>[0-9]+)/$',
        views.submit_success,
        name='submit_success'),

    url(r'^notifyURL/student-solution(?P<spsol_id>[0-9]+)/problem-result(?P<probres_id>[0-9]+)/$', views.notifyURL, name='notify'),
    # results urls
    url(
        r'^results/problem-set(?P<ps_id>[0-9]+)/problem(?P<p_id>[0-9]+)/$',
        views.results_problem_detail,
        name='results_problem_detail'),
    url(r'^results/problem-set(?P<ps_id>[0-9]+)/$',
        views.results_detail, name='results_detail'),

    #serve problem assets to admin users 
    url(r'^problem_assets/(?P<path>.*)$', views.serve_problem_asset, name='serve_problem_asset'),
]
