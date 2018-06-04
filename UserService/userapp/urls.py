from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token

from . import views

app_name = 'user_app'

urlpatterns = [
    url(r'^login/$', obtain_jwt_token),
    url(r'^logout/$', views.logout),
    url(r'^refresh/', refresh_jwt_token),
    url(r'^verify/', verify_jwt_token),
]