from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

from django.contrib import admin

from .views import version

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^hostinfo/', include('host.urls')),
    url(r'^mediawiki/', include('host.mediawiki_urls')),
    url(r'^bare/', include('host.bare_urls')),
    url(r'^_version', version),
    url(r'^api(/v1)?/', include('host.api_urls')),
    url(r'^report/', include('report.urls')),
    url(r'^hostinfo-admin/', include(admin.site.urls)),
)

urlpatterns += patterns(
    '',
    url(r'^accounts/login/', login, {'template_name': 'registration/login.html'}, name='login'),
    url(r'^accounts/logout/', logout, {'next_page': '/hostinfo/'}, name='logoff'),
)

# EOF
