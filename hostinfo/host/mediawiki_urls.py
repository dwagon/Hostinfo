"""Local URL handler for hostinfo mediawiki interface"""
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
from .mediawiki_views import (
    hosttable, hostlist, displayHost, displaySummary, doRestrValList
    )

urlpatterns = [
    path(r'^hosttable/(?P<criturl>.*?)(?P<options>/(?:order=|print=).*)?$', hosttable),
    path(r'^hostlist/(?P<criturl>.*)/$', hostlist),
    path(r'^host/(?P<hostname>\S+)$', displayHost),
    path(r'^host_summary/(?P<hostname>.*)$', displaySummary),
    path(r'^rvlist/(?P<key>\S+)/$', doRestrValList),
    ]

# EOF
