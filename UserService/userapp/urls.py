from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token

from . import views

app_name = 'user_app'

urlpatterns = [
    url(r'^login/$', obtain_jwt_token),
    url(r'^refresh/', refresh_jwt_token),
    url(r'^verify/', verify_jwt_token),
    url(r'^register/', views.register),
    url(r'^info/(?P<user_id>[0-9]+)/$', views.get_info),
    url(r'^subscribe/(?P<student_id>[0-9]+)/to/(?P<teacher_id>[0-9]+)/$', views.subscribe),
    url(r'^(?P<teacher_id>[0-9]+)/confirm/(?P<student_id>[0-9]+)/$', views.confirm),
    url(r'^(?P<teacher_id>[0-9]+)/decline/(?P<student_id>[0-9]+)/$', views.decline),
    url(r'^(?P<teacher_id>[0-9]+)/relation/(?P<student_id>[0-9]+)/$', views.has_relations),
]