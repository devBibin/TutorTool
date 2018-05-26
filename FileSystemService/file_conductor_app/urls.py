from django.conf.urls import url

from . import views

app_name = 'file_conductor_app'

urlpatterns = [
    url(r'^$', views.get_dir),
    url(r'^auth/$', views.index),
    url(r'^create/$', views.create_repo),
    url(r'^create_folder/$', views.create_folder),
    url(r'^upload_file/$', views.upload_file),
    url(r'^(?P<folder_id>[0-9]+)/$', views.get_dir),
    url(r'^(?P<parent_id>[0-9]+)/create_folder/$', views.create_folder),
    url(r'^(?P<parent_id>[0-9]+)/upload_file/$', views.upload_file),
]