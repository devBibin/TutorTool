from django.conf.urls import url

from . import views

app_name = 'gatewayapp'

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^verify/$', views.verify),
    url(r'^refresh/$', views.refresh),


    url(r'^create/$', views.create_repo),
    
    url(r'^$', views.get_folder),
    url(r'^(?P<folder_id>[0-9]+)/$', views.get_folder),
    url(r'^create_folder/$', views.create_folder),
    url(r'^create_folder/(?P<parent_id>[0-9]+)/$', views.create_folder),
    url(r'^remove_folder/(?P<id>[0-9]+)/$', views.remove_folder),

    url(r'^upload_file/$', views.upload_file),
    url(r'^upload_file/(?P<parent_id>[0-9]+)/$', views.upload_file),
    url(r'^download_file/(?P<id>[0-9]+)/$', views.download_file),
    url(r'^remove_file/(?P<id>[0-9]+)/$', views.remove_file),

    url(r'^add_question/$', views.add_question),
    url(r'^remove_question/(?P<id>[0-9]+)/$', views.remove_question),
    url(r'^question/(?P<question_id>[0-9]+)/$', views.get_question),

    url(r'^add_test/$', views.add_test),
    url(r'^remove_test/(?P<id>[0-9]+)/$', views.remove_test),
    url(r'^test/(?P<test_id>[0-9]+)/add_questions/$', views.search_for_test),
    url(r'^test/(?P<test_id>[0-9]+)/$', views.get_test),
    url(r'^test/submit/(?P<test_id>[0-9]+)/$', views.submit_test),

    url(r'^question/(?P<question_id>[0-9]+)/add/(?P<test_id>[0-9]+)/$', views.add_question_to_test),

    
    url(r'^transfer/(?P<object_type>[\w\-]+)/(?P<object_id>[0-9]+)/$', views.transfer_object),
    url(r'^transfer/$', views.submit_transfer),
    url(r'^transfer/(?P<parent_id>[0-9]+)/$', views.submit_transfer),
    
]