# hostinfo views for mediawiki interface
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2022 Dougal Scott
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

from django.http import HttpResponse
from django.shortcuts import render

from .models import KeyValue
from .models import RestrictedValue, HostinfoException

from .views import criteriaFromWeb, getHostList
from .views import orderHostList, hostData, getLinks


################################################################################
def getWikiLinks(hostid=None, hostname=None):
    wikilinks = []
    for url, tag in getLinks(hostid, hostname):
        wikilinks.append("[%s %s]" % (url, tag))
    return wikilinks


################################################################################
def displaySummary(request, hostname):
    """Display a single host"""
    d = hostData(request.user, [hostname], linker=getWikiLinks)
    return render(request, "mediawiki/hostpage.wiki", d)


################################################################################
def displayHost(request, hostname):
    """Display a single host"""
    d = hostData(request.user, [hostname], linker=getWikiLinks)
    return render(request, "mediawiki/host.wiki", d)


################################################################################
def hosttable(request, criturl, options=None):
    """Generate a table in wiki format - we can't (well, I can't)
    template this as the contents of the formatting are specified
    in the url

    options=/print=a,b,c/order=d
    """
    criteria = criteriaFromWeb(criturl)
    printers = []
    order = None
    if options:
        optlist = options[1:].split("/")
        for opt in optlist:
            if opt.startswith("print="):
                printers = opt.replace("print=", "").split(",")
            if opt.startswith("order="):
                order = opt.replace("order=", "")

    output = "{| border=1\n"
    output += "|-\n"

    hl = getHostList(criteria)
    if order:
        hl = orderHostList(hl, order)
    else:
        hl.sort()  # Sort by hostname
    output += "!Hostname\n"
    for p in printers:
        output += "!%s\n" % p.title()
    for host in hl:
        output += "|-\n"
    output += "| [[Host:%s|%s]]\n" % (host.hostname, host.hostname)
    for p in printers:
        kv = KeyValue.objects.filter(keyid__key=p, hostid=host.id)
        if len(kv) == 0:
            val = ""
        elif len(kv) == 1:
            val = kv[0].value
        else:
            val = ",".join([key.value for key in kv])
        output += "| %s\n" % val
    output += "|}\n"
    return HttpResponse(output)


################################################################################
def hostlist(request, criturl):
    """Display a list of matching hosts with their details"""
    criteria = criteriaFromWeb(criturl)
    try:
        return render(request, "mediawiki/hostlist.wiki", hostData(request, criteria))
    except HostinfoException as err:
        return render(request, "mediawiki/hostlist.wiki", {"error": err})


################################################################################
def doRestrValList(request, key):
    """Return the list of restricted values for the key"""
    rvlist = RestrictedValue.objects.filter(keyid__key=key)
    d = {"key": key, "rvlist": rvlist}
    return render(request, "mediawiki/restrval.wiki", d)


# EOF
