# hostinfo views for bare interface
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

from django.shortcuts import render

from .models import HostinfoException

from .views import getHostDetails, criteriaFromWeb
from .views import doHostDataFormat, calcKeylistVals


################################################################################
def getConfLinks(hostid=None, hostname=None):
    return []


################################################################################
def displayHost(request, hostname):
    """ Display a single host """
    d = getHostDetails(request, hostname, getConfLinks)
    return render(request, 'bare/host.html', d)


################################################################################
def doHostList(request, criturl):
    """ Display a list of matching hosts with their details"""
    qd = request.GET
    criteria = criteriaFromWeb(criturl)
    printers = qd.getlist('print', [])
    order = qd.get('order', None)
    data = doHostDataFormat(request, criteria, printers=printers, order=order)
    try:
        return render(request, 'bare/hostlist.html', data)
    except HostinfoException as err:    # pragma: no cover
        return render(request, 'bare/hostlist.html', {'error': err})


################################################################################
def doKeylist(request, key):
    d = calcKeylistVals(key)
    return render(request, 'bare/keylist.html', d)


################################################################################
def doHostcmp(request, criturl='', options=''):
    """ Display a list of matching hosts with their details"""
    criteria = criteriaFromWeb(criturl)
    try:
        return render(request, 'bare/multihost.html', doHostDataFormat(request, criteria, options))
    except HostinfoException as err:    # pragma: no cover
        return render(request, 'bare/multihost.html', {'error': err})

# EOF
