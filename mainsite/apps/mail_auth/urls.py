from django.conf.urls import patterns, url
from django.contrib import admin
import views

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^activateuser/(?P<token>.+)/$', views.activate_view),
)