# hostinfo views
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

import csv
import time

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render

from .models import Host, KeyValue, AllowedKey, parseQualifiers
from .models import RestrictedValue, HostinfoException
from .models import Links, getMatches, getHost
from .models import getAliases

_hostcache = None
_convertercache = None


################################################################################
def hostviewrepr(host, printers=[]):
    """ Return a list of KeyValue objects per key for a host
        E.g.  (('keyA',[KVobj]), ('keyB', [KVobj, KVobj, KVobj]))
    """
    kvlist = KeyValue.objects.select_related().filter(hostid__hostname=host)
    d = {}
    for kv in kvlist:
        if printers and kv.keyid.key not in printers:
            continue
        d[kv.keyid] = d.get(kv.keyid, [])
        d[kv.keyid].append(kv)
    output = []
    for k, v in list(d.items()):
        v.sort(key=lambda x: x.value)
        output.append((k.key, v))
    output.sort()
    return output


################################################################################
def handlePost(request):
    if 'hostname' in request.POST:
        return HttpResponseRedirect('/hostinfo/host/%s' % request.POST['hostname'])
    elif 'hostre' in request.POST:
        return HttpResponseRedirect('/hostinfo/hostlist/%s.hostre' % request.POST['hostre'].strip())
    elif 'key0' in request.POST:
        expr = ""
        for key in request.POST:
            if key.startswith('key'):
                num = key.replace('key', '')
                expr += "%s.%s.%s/" % (
                    request.POST['key%s' % num].strip(),
                    request.POST['op%s' % num].strip(),
                    request.POST['value%s' % num].strip().replace('/', '.slash.'))
        expr = expr[:-1]
        return HttpResponseRedirect('/hostinfo/hostlist/%s' % (expr))


################################################################################
def getLinks(hostid=None, hostname=None):
    """ Take either a hostname or a hostid and return the links for that host
    """
    if hostid:
        return [(l.url, l.tag) for l in Links.objects.filter(hostid=hostid)]
    if hostname:
        return [(l.url, l.tag) for l in Links.objects.filter(hostid__hostname=hostname)]
    return []


################################################################################
def getWebLinks(hostid=None, hostname=None):
    weblinks = []
    for url, tag in getLinks(hostid, hostname):
        weblinks.append('<a class="foreignlink" href="%s">%s</a>' % (url, tag))
    return weblinks


################################################################################
def getHostDetails(request, hostname, linker=None):
    starttime = time.time()
    host = getHost(hostname)
    if not host:
        raise Http404

    keyvals = hostviewrepr(host.hostname)
    elapsed = time.time()-starttime
    d = {
        'host': host.hostname,
        'kvlist': keyvals,
        'elapsed': "%0.4f" % elapsed,
        'user': request.user,
        'aliases': getAliases(hostname)
        }
    if linker:
        d['hostlink'] = linker(hostid=host.id)
    return d


################################################################################
def doHostSummary(request, hostname):
    """ Display a single host """
    d = getHostDetails(request, hostname, getWebLinks)
    return render(request, 'host/hostpage.template', d)


################################################################################
def doHost(request, hostname):
    """ Display a single host """
    d = getHostDetails(request, hostname, getWebLinks)
    return render(request, 'host/host.template', d)


################################################################################
def doHostDataFormat(request, criteria=[], options=''):
    starttime = time.time()
    hl = getHostList(criteria)
    data = []
    for host in hl:
        data.append((host.hostname, hostviewrepr(host.hostname), getWebLinks(hostid=host.id)))
    data.sort()
    elapsed = time.time()-starttime

    d = {
        'hostlist': data,
        'elapsed': "%0.4f" % elapsed,
        'csvavailable': '/hostinfo/csv/%s' % criteriaToWeb(criteria),
        'title': " AND ".join(criteria),
        'criteria': criteriaToWeb(criteria),
        'user': request.user,
        'count': len(data)
        }
    if options and 'dates' in options:
        d['dates'] = True
    if options and 'origin' in options:
        d['origin'] = True
    return d


################################################################################
def doHostlist(request, criturl='', options=''):
    """ Display a list of matching hosts by name only"""
    criteria = criteriaFromWeb(criturl)
    try:
        return render(request, 'host/hostlist.template', doHostDataFormat(request, criteria, options))
    except HostinfoException as err:
        return render(request, 'host/hostlist.template', {'error': err})


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
        return HttpResponseRedirect('/hostinfo/hostcmp/%s/%s' % (criturl, options[:-1]))
    try:
        return render(request, 'host/multihost.template', doHostDataFormat(request, criteria, options))
    except HostinfoException as err:
        return render(request, 'host/multihost.template', {'error': err})


################################################################################
def orderHostList(hostlist, order):
    """ Order a hostlist by the order specified
    """
    NEGATIVE = -1
    direct = 0
    if order.startswith('-'):
        direct = NEGATIVE
        order = order[1:]

    tmp = []
    for host in hostlist:
        kv = KeyValue.objects.filter(keyid__key=order, hostid=host)
        if len(kv) == 0:
            val = ""
        elif len(kv) == 1:
            val = kv[0].value
        else:
            val = ",".join([key.value for key in kv])
        tmp.append((val, host))
    tmp.sort(key=lambda x: x[0])
    if direct == NEGATIVE:
        tmp.reverse()
    hostlist = [h for v, h in tmp]
    return hostlist


################################################################################
def doCsvreport(request, criturl=''):
    criteria = criteriaFromWeb(criturl)
    hl = getHostList(criteria)
    if not criturl:
        criturl = 'allhosts'
    return csvDump(hl, '%s.csv' % criturl)


################################################################################
def criteriaToWeb(criteria):
    """ Convert a criteria list to a URL format """
    crit = "/".join([c.replace('/', '.slash.') for c in criteria])
    return crit


################################################################################
def criteriaFromWeb(criteria):
    """ Covert a URL formatted criteria to a list """
    crit = [c.replace(".slash.", '/') for c in criteria.split('/')]
    return crit


################################################################################
def getHostList(criteria):
    allhosts = {}
    for host in Host.objects.all():
        allhosts[host.id] = host

    qualifiers = parseQualifiers(criteria)
    hostids = getMatches(qualifiers)
    hosts = [allhosts[hid] for hid in hostids]
    return hosts


################################################################################
def csvDump(hostlist, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    # Convert list of hosts into all required data
    data = []
    for host in hostlist:
        data.append((host.hostname, hostviewrepr(host.hostname), None))
    data.sort(key=lambda x: x[0])

    # Grab all the headings
    hdrs = []
    hdrdict = {'hostname': 'hostname'}    # Need this for the first row of headers
    for host, details, link in data:
        for t, val in details:
            if t not in hdrs:
                hdrs.append(t)
            hdrdict[t] = t
    hdrs.sort()
    hdrs.insert(0, 'hostname')
    writer = csv.DictWriter(response, hdrs)
    writer.writerow(hdrdict)

    # Finally write the data
    for host, details, link in data:
        d = {'hostname': host}
        for t, val in details:
            d[t] = ",".join([k.value for k in val])
        writer.writerow(d)
    return response


################################################################################
def index(request):
    d = {
        'numhosts': Host.objects.count(),
        'keys': AllowedKey.objects.all(),
        'csvavailable': '/hostinfo/csv',
        'user': request.user,
    }
    return render(request, 'host/index.template', d)


################################################################################
def doRestrValList(request, key):
    """ Return the list of restricted values for the key"""
    rvlist = RestrictedValue.objects.filter(keyid__key=key)
    d = {
        'key': key,
        'rvlist': rvlist
    }
    return render(request, 'host/restrval.template', d)


################################################################################
def calcKeylistVals(key):
    kvlist = KeyValue.objects.filter(keyid__key=key).values_list('hostid', 'value')

    # Calculate the number of times each value occurs
    values = {}
    hostids = []

    for hostid, value in kvlist:
        if hostid not in hostids:
            hostids.append(hostid)
        values[value] = values.get(value, 0) + 1

    # Calculate for each distinct value percentages
    tmpvalues = []
    for k, v in list(values.items()):
        p = 100.0 * v / len(hostids)
        tmpvalues.append((k, v, p))

    tmpvalues.sort()
    total = Host.objects.count()
    numundef = total-len(hostids)
    d = {
        'key': key,
        'keylist': tmpvalues,
        'numkeys': len(tmpvalues),
        'numdef': len(hostids),
        'pctdef': 100.0*len(hostids)/total,
        'numundef': numundef,
        'pctundef': 100.0*numundef/total,
        'total': total,
    }
    return d


################################################################################
def doKeylist(request, key):
    """ Return all values for the specified key
    Need to count the number of different hosts, not different values to work out
    percentages otherwise you get wierd values for list keys.
    Also do other key funkiness
    """
    starttime = time.time()
    d = calcKeylistVals(key)
    d['elapsed'] = "%0.4f" % (time.time() - starttime)
    d['user'] = request.user
    return render(request, 'host/keylist.template', d)

# EOF
