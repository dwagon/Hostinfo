#
# URL manager for top level
#
# $Id: urls.py 159 2013-06-23 05:02:56Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/hostinfo/urls.py $
#
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^hostinfo/', include('hostinfo.host.urls')),
    url(r'^hostinfo-admin/', include(admin.site.urls)),

)

#EOF
