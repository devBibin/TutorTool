from django.conf.urls import url

from . import views

app_name = 'user_app'

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
]