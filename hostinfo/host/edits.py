# hostinfo edit code
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

import re
import time

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Host, KeyValue, AllowedKey
from .models import getAK, RestrictedValue
from .models import getHost, validateDate
from .models import RestrictedValueException

from .forms import hostMergeForm, hostRenameForm, hostCreateForm
from .forms import hostEditForm

from .views import hostviewrepr

_hostcache = None
_convertercache = None


################################################################################
def getHostMergeKeyData(srchost, dsthost):
    # Get the list of all keys that either or both of the hosts have
    # Force everything to be a list as it is easier than trying
    # to do type differentiation in the template
    keydata = {}
    srckeys = KeyValue.objects.filter(hostid=srchost)
    dstkeys = KeyValue.objects.filter(hostid=dsthost)
    for key in srckeys:
        keyname = key.keyid.key
        if keyname not in keydata:
            keydata[keyname] = {'src': [key.value], 'dst': []}
        else:
            keydata[keyname]['src'].append(key.value)

    for key in dstkeys:
        keyname = key.keyid.key
        if keyname not in keydata:
            keydata[keyname] = {'src': [], 'dst': [key.value]}
        else:
            keydata[keyname]['dst'].append(key.value)

    keys = []
    for key, val in list(keydata.items()):
        keys.append((key, val))
    keys.sort()
    return keys


################################################################################
def mergeKey(request, srchostobj, dsthostobj, key):
    keyobj = AllowedKey.objects.get(key=key)
    if keyobj.get_validtype_display() == 'list':
        srckeys = KeyValue.objects.filter(hostid=srchostobj, keyid=keyobj)
        dstkeys = KeyValue.objects.filter(hostid=dsthostobj, keyid=keyobj)
        for dkey in dstkeys:
            dkey.delete(request.user)
        for skey in srckeys:
            skey.hostid = dsthostobj
            skey.save(request.user)
    else:
        try:
            dstval = KeyValue.objects.get(hostid=dsthostobj, keyid=keyobj)
            dstval.delete(request.user)
        except ObjectDoesNotExist:
            pass
        srcval = KeyValue.objects.get(hostid=srchostobj, keyid=keyobj)
        srcval.hostid = dsthostobj
        srcval.save(request.user)


################################################################################
@login_required
def doHostMerging(request):
    """ Actually perform the merge
        We use underscores to avoid any future clash with keys that may be picked
    """
    srchost = request.POST['_srchost']
    srchostobj = Host.objects.get(hostname=srchost)
    dsthost = request.POST['_dsthost']
    dsthostobj = Host.objects.get(hostname=dsthost)
    for key in request.POST:
        if key.startswith('_'):
            continue
        if request.POST[key] == 'src':   # DST happens automatically
            mergeKey(request, srchostobj, dsthostobj, key)
    srchostobj.delete()


################################################################################
@login_required
def doHostMergeChoose(request):
    """Get the user to choose hosts to merge
    """
    starttime = time.time()
    d = {}
    if request.method == 'POST':
        form = hostMergeForm(request.POST)
        d['form'] = form
        if form.is_valid():
            srchost = form.cleaned_data['srchost']
            dsthost = form.cleaned_data['dsthost']
            return HttpResponseRedirect('/hostinfo/hostmerge/%s/%s' % (srchost, dsthost))
    else:
        d['form'] = hostMergeForm()
    d['elapsed'] = time.time()-starttime
    return render(request, 'host/hostmerge.template', d)


################################################################################
@login_required
def doHostMerge(request, srchost, dsthost):
    """Prepare the various forms for doing host merges
    """
    starttime = time.time()
    d = {}
    d['srchost'] = srchost
    d['dsthost'] = dsthost
    if '_hostmerging' in request.POST:
        # User has selected which bits to merge
        doHostMerging(request)
        d['merged'] = True
    else:
        d['keys'] = getHostMergeKeyData(getHost(srchost), getHost(dsthost))
        d['merging'] = True
    d['elapsed'] = time.time()-starttime
    return render(request, 'host/hostmerge.template', d)


################################################################################
@login_required
def doHostRenameChoose(request):
    """Get the user to choose a host to rename
    """
    starttime = time.time()
    d = {}
    if request.method == 'POST':
        form = hostRenameForm(request.POST)
        d['form'] = form
        if form.is_valid():
            srchost = form.cleaned_data['srchost']
            dsthost = form.cleaned_data['dsthost']
            return HttpResponseRedirect('/hostinfo/hostrename/%s/%s' % (srchost, dsthost))
    else:
        d['form'] = hostRenameForm()
    d['elapsed'] = time.time()-starttime
    return render(request, 'host/hostrename.template', d)


################################################################################
@login_required
def doHostRename(request, srchost, dsthost):
    starttime = time.time()
    d = {}
    d['srchost'] = srchost
    d['dsthost'] = dsthost
    srchost = Host.objects.get(hostname=srchost)
    srchost.hostname = dsthost
    srchost.save(request.user)
    d['renamed'] = True
    d['elapsed'] = time.time()-starttime
    return render(request, 'host/hostrename.template', d)


################################################################################
@login_required
def doHostCreateChoose(request):
    """
        Get the user to choose a host to create
    """
    starttime = time.time()
    d = {}
    if request.method == 'POST':
        form = hostCreateForm(request.POST)
        d['form'] = form
        if form.is_valid():
            hostname = form.cleaned_data['newhost']
            return HttpResponseRedirect('/hostinfo/hostcreate/%s' % hostname)
    else:
        d['form'] = hostCreateForm()
    d['elapsed'] = time.time()-starttime
    return render(request, 'host/hostcreate.template', d)


################################################################################
@login_required
def doHostCreate(request, hostname):
    starttime = time.time()
    d = {}
    d['newhost'] = hostname
    nh = Host(hostname=hostname)
    nh.save(request.user)
    d['created'] = True
    d['elapsed'] = time.time()-starttime
    return render(request, 'host/hostcreate.template', d)


################################################################################
@login_required
def doHostEditChoose(request):
    """Get the user to choose a host to edit
    """
    starttime = time.time()
    d = {}
    if request.method == 'POST':
        form = hostEditForm(request.POST)
        d['form'] = form
        if form.is_valid():
            hostname = form.cleaned_data['hostname']
            return HttpResponseRedirect('/hostinfo/hostedit/%s' % hostname)
    else:
        d['form'] = hostEditForm()
    d['elapsed'] = time.time() - starttime
    return render(request, 'host/hostedit.template', d)


################################################################################
@login_required
def doHostEdit(request, hostname):
    starttime = time.time()
    d = {}
    if '_hostediting' in request.POST:
        # User has selected which bits to change
        try:
            doHostEditChanges(request, hostname)
        except RestrictedValueException as err:
            reslist = [v[0] for v in RestrictedValue.objects.filter(keyid=err.key).values_list('value')]
            reserr = ", ".join(reslist)
            d['errorbig'] = err
            d['errorsmall'] = "Please pick one of: %s" % reserr
        else:
            return HttpResponseRedirect('/hostinfo/host/%s' % hostname)
    # User has selected which host to change
    keyvals = hostviewrepr(hostname)
    kvlist = []
    usedkeys = set()
    for key, vals in keyvals:
        usedkeys.add(key)
        vtype = getAK(key).get_validtype_display()
        if getAK(key).restrictedFlag:
            reslist = [v[0] for v in RestrictedValue.objects.filter(keyid__key=key).values_list('value')]
            reslist.insert(0, '-Unknown-')
        else:
            reslist = []
        kvlist.append((key, vals, vtype, reslist))

    # Don't let them create a new keyvalue for one that already exists
    keylist = [k for k in AllowedKey.objects.all() if k.key not in usedkeys]
    d['kvlist'] = kvlist
    d['host'] = hostname
    d['keylist'] = keylist
    d['editing'] = True
    d['elapsed'] = time.time()-starttime
    return render(request, 'host/hostedit.template', d)


################################################################################
@login_required
def doHostEditChanges(request, hostname):
    hostobj = Host.objects.get(hostname=hostname)
    listdata = {}
    newkey = None
    newval = None
    for k, v in list(request.POST.items()):
        if k == '_newkey.new':
            newkey = AllowedKey.objects.get(key=v)
        if k == '_newvalue.new':
            newval = v
    if newkey and newval:
        kv = KeyValue(hostid=hostobj, keyid=newkey, value=newval, origin='webform')
        kv.save(request.user)
    for k, v in list(request.POST.items()):
        if k.startswith('_'):
            continue
        # An existing key is being edited
        m = re.match('(?P<key>\D+)\.(?P<instance>[\d+|new])', k)
        if not m:
            continue
        key = m.group('key')
        # instance = m.group('instance')
        newvalue = str(v)

        keyobj = AllowedKey.objects.get(key=key)
        if keyobj.get_validtype_display() == 'list':
            if key not in listdata:
                listdata[key] = []
            if newvalue and newvalue != '-Unknown-':
                listdata[key].append(newvalue)
        else:
            if keyobj.get_validtype_display() == 'date':
                newvalue = validateDate(newvalue)

        # If the value is the same - no change; blank - delete; different - new value
        keyval = KeyValue.objects.get(keyid=keyobj, hostid=hostobj)
        if newvalue == '':
            keyval.delete(request.user)
        elif newvalue == keyval.value:
            pass     # No change
        else:
            keyval.value = newvalue
            keyval.save(request.user)

    # Now we have to go through the lists to work out what the new values should be
    for key in listdata:
        existingvals = [str(k.value) for k in KeyValue.objects.filter(keyid__key=key, hostid=hostobj)]
        keyobj = AllowedKey.objects.get(key=key)

        for val in listdata[key]:
            if val not in existingvals:
                kv = KeyValue(hostid=hostobj, keyid=keyobj, value=val, origin='webform')
                kv.save(request.user)

        for val in existingvals:
            if val not in listdata[key]:
                kv = KeyValue.objects.get(hostid=hostobj, keyid=keyobj, value=val)
                kv.delete(request.user)


# EOF
