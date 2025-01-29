"""Local URL handler for hostinfo"""
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2025 Dougal Scott
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
from .views import index, doHostlist, doHost, doKeylist, handlePost
from .views import doHostcmp, doHostSummary, doCsvreport, doRestrValList
from .edits import (
    doHostMerge,
    doHostMergeChoose,
    doHostRenameChoose,
    doHostEditChoose,
    doHostCreateChoose,
    doHostEdit,
    doHostCreate,
    doHostRename,
)


urlpatterns = [
    path("", index, name="index"),
    path("handlePost/", handlePost, name="formhandler"),
    path("hostedit/", doHostEditChoose, name="hostEditChoose"),
    path("hostedit/<str:hostname>/", doHostEdit, name="hostEdit"),
    path("hostcreate/", doHostCreateChoose, name="hostCreateChoose"),
    path("hostcreate/<str:hostname>/", doHostCreate, name="hostCreate"),
    path("hostmerge/", doHostMergeChoose, name="hostMergeChoose"),
    path("hostmerge/<str:srchost>/<str:dsthost>", doHostMerge, name="hostMerge"),
    path("hostrename/", doHostRenameChoose, name="hostRenameChoose"),
    path(
        "hostrename/<str:srchost>/<str:dsthost>",
        doHostRename,
        name="hostRename",
    ),
    re_path("hostlist/(?P<criturl>.*)/(?P<options>opts=.*)?$", doHostlist),
    path("hostlist/", doHostlist, name="hostlist"),
    re_path("hostcmp/(?P<criturl>.*)/(?P<options>opts=.*)?$", doHostcmp),
    path("hostcmp/", doHostcmp),
    path("host/<str:hostname>/", doHost, name="host"),
    path("host/", doHostlist),
    path("host_summary/<str:hostname>", doHostSummary),
    path("csv/", doCsvreport),
    path("csv/<str:criturl>/", doCsvreport),
    path("keylist/<str:key>/", doKeylist, name="keylist"),
    path("rvlist/<str:key>/", doRestrValList),
]

# EOF
