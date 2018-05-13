from django.conf.urls import url

from . import views

app_name = 'file_conductor_app'

urlpatterns = [
    url(r'^$', views.index),
    url(r'^upload/$', views.upload),
]