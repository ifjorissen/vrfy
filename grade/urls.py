from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^assignment/add/$', views.AssignmentCreate.as_view(), name='assignment_add')
    ]
