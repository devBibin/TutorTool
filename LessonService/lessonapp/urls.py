from django.conf.urls import url

from . import views

app_name = 'lessonapp'

urlpatterns = [
    url(r'^add/(?P<teacher_id>[0-9]+)/for/(?P<student_id>[0-9]+)/$', views.add_lesson),
    url(r'^(?P<object_type>[\w\-]+)/(?P<object_id>[0-9]+)/to/(?P<lesson_id>[0-9]+)/$', views.add_homework_item),
    url(r'^get/(?P<teacher_id>[0-9]+)/(?P<student_id>[0-9]+)/$', views.get_lessons), 
    url(r'^(?P<student_id>[0-9]+)/to/(?P<object_type>[\w\-]+)/(?P<object_id>[0-9]+)/$', views.has_student_access),    
]