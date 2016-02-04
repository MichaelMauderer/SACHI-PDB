from django.conf.urls import patterns, url
from django.contrib import admin
import views

admin.autodiscover()

urlpatterns = patterns('',

     url(r'^$', views.public_add_participant, name='addparticipant_public'),
     url(r'^addparticipant/$', views.private_add_participant, name='addparticipant'),
     url(r'^unsubscribe/(?P<token>.+)/$', views.unsubscribe_view, name='unsubscribe'),
     url(r'^activate/(?P<token>.+)/$', views.activate_view, name='activate'),
     url(r'^sendmessage/$', views.send_message_view, name='sendmessage'),
   
)