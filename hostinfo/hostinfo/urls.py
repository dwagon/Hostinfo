from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^hostinfo/', include('host.urls')),
    url(r'^hostinfo-admin/', include(admin.site.urls)),
)
