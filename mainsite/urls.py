from django.conf.urls import patterns, include, url
from django.contrib import admin
from mainsite.views import UserCreate

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('mainsite.apps.participantdatabase.urls')),
    url(r'^', include('mainsite.apps.mail_auth.urls')),
    url(r'^requestaccess/$', UserCreate.as_view(),
        name='requestaccess',
        ),

    url(r'^login/', 'django.contrib.auth.views.login',
        {'template_name': 'login.html',
         'redirect_field_name': 'addparticipant'},
        name='login',
        ),
    url(r'^logout/', 'django.contrib.auth.views.logout',
        {'next_page': '/login'},
        name='logout',
        ),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
