from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^hostinfo/', include('host.urls')),
    url(r'^report/', include('report.urls')),
    url(r'^hostinfo-admin/', include(admin.site.urls)),
)

urlpatterns += patterns(
    '',
    url(r'^accounts/login/', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout', {'next_page': '/hostinfo/'}, name='logoff'),
)

# EOF
