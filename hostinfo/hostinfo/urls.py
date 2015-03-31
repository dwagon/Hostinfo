from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^hostinfo/', include('host.urls')),
    url(r'^api(/v1)?/', include('host.apiurls')),
    url(r'^report/', include('report.urls')),
    url(r'^hostinfo-admin/', include(admin.site.urls)),
)

urlpatterns += patterns(
    '',
    url(r'^accounts/login/', login, {'template_name': 'registration/login.html'}, name='login'),
    url(r'^accounts/logout/', logout, {'next_page': '/hostinfo/'}, name='logoff'),
)

# EOF
