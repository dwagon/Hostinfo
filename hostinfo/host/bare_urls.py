"""Local URL handler for hostinfo bare interface"""
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2015 Dougal Scott
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
from .bare_views import (
    displayHost, doHostCount, doHostList, doHostcmp, doKeylist
    )

urlpatterns = [
    path(r'^hostlist/(?P<criturl>.*)/?$', doHostList),
    path(r'^count/(?P<criturl>.*)/?$', doHostCount),
    path(r'^host/(?P<hostname>\S+)/?$', displayHost),
    path(r'^keylist/(?P<key>\S+?)/(?P<criturl>.*)?/?$', doKeylist),
    path(r'^hostcmp/(?P<criturl>.*)/(?P<options>opts=.*)?/?$', doHostcmp),
    path(r'^hostcmp/?$', doHostcmp),
    ]

# EOF
