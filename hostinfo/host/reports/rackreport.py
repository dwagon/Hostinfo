#!/usr/bin/env python
# 
# Script to generate a rack report for hostinfo
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: rackreport.py 159 2013-06-23 05:02:56Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/hostinfo/host/reports/rackreport.py $

import re
import time
import sys
from django.shortcuts import render_to_response
from hostinfo.host.models import Host, KeyValue, getAkCache

################################################################################
reportname="Rack Reports"
reportdesc="Report on what hosts are in which racks"

################################################################################
def doReport(request, args):
    if args=='':
    	return doRackreport(request)
    m=re.match(r'^(?P<site>\w+)$', args)
    if m:	
    	return doRackreport(request, **m.groupdict())
    m=re.match(r'^(?P<site>\w+)/(?P<rack>\S+)$', args)
    if m:	
    	return doRackreport(request, **m.groupdict())
    sys.stderr.write("Unmatched args=%s\n" % args)

################################################################################
def doRackList(request):
    """ Report the list of sites that have racks as no site has been specified
    """
    starttime=time.time()
    kvlist=KeyValue.objects.filter(keyid__key='site')
    values={}
    for kv in kvlist:
	values[kv.value]=1
    tmpvalues=[k for k,v in values.items()]
    tmpvalues.sort()
    tmpvalues.append('No_site_known')
    elapsed=time.time()-starttime
    d={
	'keylist': tmpvalues,
	'elapsed':"%0.4f" % elapsed,
	'user': request.user,
	}
    return render_to_response('racklist.template', d)

################################################################################
def doRackreport(request, site='', rack=''):
    """ Generate a report on what should be in each rack - useful for a
    physical audit

    If no site specified, return a list of sites to report on
    """
    starttime=time.time()
    urlrack=rack	# Convert to a better variable name
    urlsite=site

    # Get the list of sites that exist for the initial overview page
    if not urlsite:
    	return doRackList(request)

    # Prepare a dictionary of all known hosts
    hostdict={}
    hosts=Host.objects.all()
    for host in hosts:
    	hostdict[host.id]=host.hostname

    # Remove all type=virtual
    virtuals=[kv.hostid for kv in KeyValue.objects.filter(keyid__key='type', value='virtual')]
    for host in virtuals:
	del hostdict[host.id]

    if urlsite=='No_site_known':
	# Remove all hosts that do have a site
	knownhosts=KeyValue.objects.filter(keyid__key='site').values('hostid')
	knownids=[kh['hostid'] for kh in knownhosts]
	for hostid in knownids:
	    if hostid in hostdict:
		del hostdict[hostid]
    else:
	# Remove hostids that aren't in the rack in question, if there is a rack
	if urlrack:
	    rackhosts=KeyValue.objects.filter(keyid__key='rack', value=urlrack).values('hostid')
	    rackids=[rh['hostid'] for rh in rackhosts]
	    for hostid in hostdict.keys():
		if hostid not in rackids:
		    del hostdict[hostid]

	# Remove hostids that aren't in the site in question
	sitehosts=KeyValue.objects.filter(keyid__key='site', value=urlsite).values('hostid')
	siteids=[sh['hostid'] for sh in sitehosts]
	for hostid in hostdict.keys():
	    if hostid not in siteids:
		del hostdict[hostid]

    akcache=getAkCache()
    revak={}
    for ak in akcache:
    	revak[akcache[ak].id]=ak

    # Populate rack data with everything known about the hosts that are left
    # data[rack][host][allowedkey]=value
    data={}
    for id,hostname in hostdict.items():
    	kvlist=KeyValue.objects.filter(hostid=id).values()
	try:
	    rack=[o['value'] for o in kvlist if o['keyid_id']==akcache['rack'].id][0]
	except IndexError:
	    rack='_undefined_'
	if rack not in data:
	    data[rack]={}
	data[rack][hostname]={}
	for kvd in kvlist:
	    key=revak[kvd['keyid_id']]
	    val=kvd['value']
	    data[rack][hostname][key]=val

    # Convert to a list format that can be sorted
    datalist=[]
    for rack in data:
	tmphostlist=[]
    	for host in data[rack]:
	    tmphostlist.append((host,data[rack][host]))
	tmphostlist.sort()
	datalist.append((rack,tmphostlist))
    datalist.sort()

    elapsed=time.time()-starttime
    d={ 'site': urlsite,
    	'rack': urlrack,
	'data': datalist,
	'elapsed': "%0.4f" % elapsed,
	'numracks': len(data),
	'numitems': len(hostdict),
	'user': request.user,
    	}

    return render_to_response('rackreport.template', d)

#EOF
