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

from django.urls import path, re_path
from .mediawiki_views import (
    hosttable,
    hostlist,
    displayHost,
    displaySummary,
    doRestrValList,
)

urlpatterns = [
    re_path("hosttable/<str:criturl>(?P<options>/(?:order=|print=).*)?$", hosttable),
    path("hostlist/<str:criturl>", hostlist),
    path("host/<str:hostname>", displayHost),
    path("host_summary/<str:hostname>", displaySummary),
    path("rvlist/<str:key>)/", doRestrValList),
]

# EOF
