from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^open/$', views.openTngo, name='open')#called openTngo as to not overwrite the building in function open()
    ]
