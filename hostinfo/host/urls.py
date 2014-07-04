# Local URL handled for hostinfo
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2014 Dougal Scott
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import patterns, url
import django.contrib.auth.views

urlpatterns=patterns('host.views',
    (r'^$', 'index'),
    (r'^handlePost/$', 'handlePost'),

    (r'^hostedit/$', 'doHostEditChoose'),
    (r'^hostedit/(?P<hostname>\S+)/$', 'doHostEdit'),

    (r'^hostcreate/$', 'doHostCreateChoose'),
    (r'^hostcreate/(?P<hostname>\S+)/$', 'doHostCreate'),

    (r'^hostmerge/$', 'doHostMergeChoose'),
    (r'^hostmerge/(?P<srchost>\S+)/(?P<dsthost>\S+)$', 'doHostMerge'),

    (r'^hostrename/$', 'doHostRenameChoose'),
    (r'^hostrename/(?P<srchost>\S+)/(?P<dsthost>\S+)$', 'doHostRename'),

    (r'^hostlist/(?P<criteria>.*)/(?P<options>opts=.*)?$', 'doHostlist'),
    (r'^hostcmp/(?P<criteria>.*)/(?P<options>opts=.*)?$', 'doHostcmp'),
    (r'^hostwikitable/(?P<criteria>.*?)(?P<options>/(?:order=|print=).*)?$', 'doHostwikiTable'),
    (r'^hostwiki/(?P<criteria>.*)/$', 'doHostwiki'),
    (r'^host/$', 'doHostlist'),
    (r'^host/(?P<hostname>\S+)/$', 'doHost'),
    (r'^host/(?P<hostname>\S+)/wiki$', 'doHost', {'format':'wiki'}),
    (r'^host_summary/(?P<hostname>.*)/(?P<format>\S+)$', 'doHostSummary'),
    (r'^host_summary/(?P<hostname>.*)$', 'doHostSummary'),
    (r'^csv/$', 'doCsvreport'),
    (r'^csv/(?P<criteria>.*)/$', 'doCsvreport'),
    (r'^keylist/(?P<key>\S+)/$', 'doKeylist'),
    (r'^rvlist/(?P<key>\S+)/$', 'doRestrValList'),
    (r'^rvlist/(?P<key>\S+)/(?P<mode>\S+)$', 'doRestrValList'),
    )

urlpatterns+=patterns('',
    (r'^accounts/login/', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/', 'django.contrib.auth.views.logout', {'next_page': '/hostinfo/'}),
    )

#EOF
