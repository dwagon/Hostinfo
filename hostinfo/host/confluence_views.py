# hostinfo views for confluence interface
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

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import KeyValue
from .models import RestrictedValue, HostinfoException

from .views import getHostDetails, criteriaFromWeb, getHostList
from .views import orderHostList, doHostDataFormat, getLinks, calcKeylistVals


################################################################################
def getConfLinks(hostid=None, hostname=None):
    conflinks = []
    for url, tag in getLinks(hostid, hostname):
        conflinks.append('[%s %s]' % (url, tag))
    return conflinks


################################################################################
def displaySummary(request, hostname):
    """ Display a single host """
    d = getHostDetails(request, hostname, getConfLinks)
    return render(request, 'confluence/hostpage.html', d)


################################################################################
def displayHost(request, hostname):
    """ Display a single host """
    d = getHostDetails(request, hostname, getConfLinks)
    return render(request, 'confluence/host.html', d)


################################################################################
def doHostList(request, criturl):
    """ Display a list of matching hosts with their details"""
    criteria = criteriaFromWeb(criturl)
    d = doHostDataFormat(request, criteria)
    try:
        return render(request, 'confluence/hostlist.html', d)
    except HostinfoException as err:
        return render(request, 'confluence/hostlist.html', {'error': err})


################################################################################
def doKeylist(request, key):
    d = calcKeylistVals(key)
    return render(request, 'confluence/keylist.html', d)


################################################################################
def doRestrValList(request, key):
    """ Return the list of restricted values for the key"""
    rvlist = RestrictedValue.objects.filter(keyid__key=key)
    d = {
        'key': key,
        'rvlist': rvlist
    }
    return render(request, 'confluence/restrval.html', d)


################################################################################
def doHostcmp(request, criturl='', options=''):
    """ Display a list of matching hosts with their details"""
    criteria = criteriaFromWeb(criturl)
    if request.method == 'POST' and 'options' in request.POST:
        options = 'opts='
        if 'dates' in request.POST.getlist('options'):
            options += 'dates,'
        if 'origin' in request.POST.getlist('options'):
            options += 'origin,'
        return HttpResponseRedirect('/confluence/hostcmp/%s/%s' % (criturl, options[:-1]))
    try:
        return render(request, 'confluence/multihost.html', doHostDataFormat(request, criteria, options))
    except HostinfoException as err:
        return render(request, 'confluence/multihost.html', {'error': err})


# EOF
