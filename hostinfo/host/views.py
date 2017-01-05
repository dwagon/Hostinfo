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
import operator
import time
from collections import defaultdict

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import Host, KeyValue, AllowedKey, calcKeylistVals
from .models import RestrictedValue, HostinfoException
from .models import Links, getHostList, getAliases, getAK


################################################################################
def hostviewrepr(host, printers=[]):
    """ Return a list of KeyValue objects per key for a host
        E.g.  (('keyA',[KVobj]), ('keyB', [KVobj, KVobj, KVobj]), ('keyC',[]))
    """
    revcache = {}
    for aks in AllowedKey.objects.all():
        revcache[aks.id] = aks.key

    kvlist = KeyValue.objects.filter(hostid__hostname=host)
    kvdict = defaultdict(list)
    for kv in kvlist:
        kvdict[revcache[kv.keyid_id]].append(kv)

    if not printers:
        printers = sorted(kvdict.keys())

    output = []
    for pr in printers:
        tmp = kvdict.get(pr, [])
        tmp.sort(key=lambda x: x.value)
        output.append((pr, tmp))
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
def doHostSummary(request, hostname):
    """ Display a single host """
    d = hostData(request.user, [hostname], linker=getWebLinks)
    return render(request, 'host/hostpage.template', d)


################################################################################
def doHost(request, hostname):
    """ Display a single host """
    d = hostData(request.user, [hostname], linker=getWebLinks)
    return render(request, 'host/host.template', d)


################################################################################
def hostCount(user, criteria=[]):
    """ Count number of matching hosts """
    starttime = time.time()
    hl = getHostList(criteria)
    elapsed = time.time()-starttime

    d = {
        'elapsed': "%0.4f" % elapsed,
        'title': " AND ".join(criteria),
        'criteria': criteriaToWeb(criteria),
        'user': user,
        'count': len(hl),
        }
    return d


################################################################################
def hostData(user, criteria=[], options='', printers=[], order=None, linker=None):
    """ Convert criteria and other options into a consistent data format
    for consumption in the templates """
    starttime = time.time()
    hl = getHostList(criteria)
    if order:
        hl = orderHostList(hl, order)
    else:
        hl = sorted(hl, key=operator.attrgetter('hostname'))
    data = []
    for host in hl:
        tmp = {
            'hostname': host.hostname,
            'hostview': hostviewrepr(host.hostname, printers=printers),
            'aliases': getAliases(host.hostname)
            }
        if linker:
            tmp['links'] = linker(hostid=host.id)
        data.append(tmp)

    elapsed = time.time()-starttime

    d = {
        'hostlist': data,
        'elapsed': "%0.4f" % elapsed,
        'csvavailable': '/hostinfo/csv/%s' % criteriaToWeb(criteria),
        'title': " AND ".join(criteria),
        'criteria': criteriaToWeb(criteria),
        'user': user,
        'count': len(data),
        'printers': printers,
        'order': order,
        'options': options,
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
        return render(request, 'host/hostlist.template', hostData(request.user, criteria, options))
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
        return render(request, 'host/multihost.template', hostData(request.user, criteria, options))
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
    ak = getAK(key=order)
    for host in hostlist:
        kv = KeyValue.objects.filter(keyid=ak, hostid=host)
        if len(kv) == 0:
            val = ""
        elif len(kv) == 1:
            if ak.numericFlag:
                val = kv[0].numvalue
            else:
                val = kv[0].value
        else:
            if ak.numericFlag:
                val = ",".join([key.numvalue for key in kv])
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
    crit = [c.replace(".slash.", '/') for c in criteria.split('/') if c]
    return crit


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
def doKeylist(request, key):
    """ Return all values for the specified key
    Need to count the number of different hosts, not different values to work out
    percentages otherwise you get wierd values for list keys.
    Also do other key funkiness
    """
    starttime = time.time()
    d = {}
    try:
        d = calcKeylistVals(key)
    except HostinfoException as exc:
        d['error'] = exc
    d['elapsed'] = "%0.4f" % (time.time() - starttime)
    d['user'] = request.user
    return render(request, 'host/keylist.template', d)

# EOF
