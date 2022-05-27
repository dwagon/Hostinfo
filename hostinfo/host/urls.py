# Local URL handler for hostinfo
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

from django.urls import path
from .views import index, doHostlist, doHost, doKeylist, handlePost
from .views import handlePost, doHostcmp, doHostSummary, doCsvreport, doRestrValList
from .edits import (
    doHostMerge, doHostMergeChoose, doHostRenameChoose, doHostEditChoose,
    doHostCreateChoose, doHostEdit, doHostCreate, doHostRename
    )


urlpatterns = [
    path(r'^$', index, name='index'),
    path(r'^handlePost/$', handlePost, name='formhandler'),

    path(r'^hostedit/$', doHostEditChoose, name='hostEditChoose'),
    path(r'^hostedit/(?P<hostname>\S+)/$', doHostEdit, name='hostEdit'),

    path(r'^hostcreate/$', doHostCreateChoose, name='hostCreateChoose'),
    path(r'^hostcreate/(?P<hostname>\S+)/$', doHostCreate, name='hostCreate'),

    path(r'^hostmerge/$', doHostMergeChoose, name='hostMergeChoose'),
    path(r'^hostmerge/(?P<srchost>\S+)/(?P<dsthost>\S+)$', doHostMerge, name='hostMerge'),

    path(r'^hostrename/$', doHostRenameChoose, name='hostRenameChoose'),
    path(r'^hostrename/(?P<srchost>\S+)/(?P<dsthost>\S+)$', doHostRename, name='hostRename'),

    path(r'^hostlist/(?P<criturl>.*)/(?P<options>opts=.*)?$', doHostlist),
    path(r'^hostlist/$', doHostlist, name='hostlist'),
    path(r'^hostcmp/(?P<criturl>.*)/(?P<options>opts=.*)?$', doHostcmp),
    path(r'^hostcmp/$', doHostcmp),
    path(r'^host/(?P<hostname>\S+)/$', doHost, name='host'),
    path(r'^host/$', doHostlist),
    path(r'^host_summary/(?P<hostname>.*)$', doHostSummary),
    path(r'^csv/$', doCsvreport),
    path(r'^csv/(?P<criturl>.*)/$', doCsvreport),
    path(r'^keylist/(?P<key>\S+)/$', doKeylist, name='keylist'),
    path(r'^rvlist/(?P<key>\S+)/$', doRestrValList),
    ]

# EOF
