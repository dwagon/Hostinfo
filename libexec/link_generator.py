#!/bin/env python
# 
# Script to populate the links table 
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: link_generator.py 125 2012-12-05 21:18:29Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/libexec/link_generator.py $
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

import os, sys, getopt, time
os.environ['DJANGO_SETTINGS_MODULE']='hostinfo.settings'
os.environ['PATH']+=":/usr/local/bin"
from hostinfo.hostinfo.models import Host, Links
from django.core.exceptions import ObjectDoesNotExist

verbFlag=False
kiddingFlag=False
link_path='/usr/local/lib/hostinfo/links.d'

################################################################################
def getLinkPrograms(bulk=False):
    link_progs=[]
    if not os.path.exists(link_path):
    	fatal("No link directory (%s) exists" % link_path)
    for lf in os.listdir(link_path):
	ff=os.path.join(link_path,lf)
	if not os.path.isfile(ff):
	    continue
	if os.access(ff,os.X_OK):
	    if lf.startswith('bulk_') and bulk:
		link_progs.append(ff)
	    elif not lf.startswith('bulk_') and not bulk:
		link_progs.append(ff)
    return link_progs

################################################################################
def getLinks(link_prog, hostname=None):
    """ Run the link generating program link_prog
    """
    links=[]
    verbose("Running %s" % link_prog)
    if not hostname:
	f=os.popen("%s" % link_prog)
    else:
	f=os.popen("%s %s" % (link_prog, hostname))
    output=f.readlines()
    x=f.close()
    if x:		# Only use the output if it returned success
	return []

    for line in output:
	line=line.strip()
	bits=line.split()
	if hostname:
	    bit=[hostname, bits[0], " ".join(bits[1:])]
	else:
	    bit=[bits[0], bits[1], " ".join(bits[2:])]
	links.append(bit)

    return links

################################################################################
def verbose(msg):
    if verbFlag:
    	sys.stderr.write("%s\n" % msg)

################################################################################
def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)

################################################################################
def fatal(msg):
    sys.stderr.write("Fatal: %s\n" % msg)
    sys.exit(255)

################################################################################
def usage():
    sys.stderr.write("Usage: %s\n" % sys.argv[0])

################################################################################
def saveLink(host, tag, url):
    hostid=Host.objects.get(hostname=host)
    verbose("Adding %s to %s" % (tag, host))
    l=Links(hostid=hostid, url=url, tag=tag)
    if not kiddingFlag:
	l.save()

################################################################################
def deleteLink(host, tag):
    hostid=Host.objects.get(hostname=host)
    link=Links.objects.get(hostid=hostid, tag=tag)
    verbose("Deleting %s link for %s" % (tag, host))
    if not kiddingFlag:
	link.delete()

################################################################################
def updateLink(host, tag, url):
    hostid=Host.objects.get(hostname=host)
    verbose("Updating %s on %s" % (tag, host))
    l=Links.objects.get(hostid=hostid, tag=tag)
    l.url=url
    if not kiddingFlag:
	l.save()

################################################################################
def loadLinkList(hostlist):
    linkdump={}
    for l in Links.objects.all():
    	if l.hostid.hostname in hostlist:
	    if l.hostid.hostname not in linkdump:
	    	linkdump[l.hostid.hostname]={}
	    linkdump[l.hostid.hostname][l.tag]=l.url
    return linkdump

################################################################################
def updateLinks(hostlist, oldlinks, newlinks):
    for host in hostlist:
    	if host in oldlinks:
	    for tag in oldlinks[host].keys():
		if host not in newlinks or tag not in newlinks[host]:
		    deleteLink(host, tag)
		elif oldlinks[host][tag]!=newlinks[host][tag]:
		    updateLink(host, tag, newlinks[host][tag])
		else:
		    verbose("Keeping %s for %s" % (tag, host))
	for tag in newlinks[host].keys():
	    if host not in oldlinks or tag not in oldlinks[host]:
		saveLink(host, tag, newlinks[host][tag])

################################################################################
def main(hostlist):
    if not hostlist:
    	hl=Host.objects.all()
	hostlist=[h.hostname for h in hl]

    oldlinks=loadLinkList(hostlist)
    newlinks={}

    # Get normal updaters
    link_progs=getLinkPrograms(bulk=False)
    for host in hostlist:
    	verbose("Getting links for %s" % host)
	try:
	    for link_prog in link_progs:
		linklist=getLinks(link_prog, host)
		for hn,lu,lt in linklist:
		    if hn not in newlinks:
		    	newlinks[hn]={}
		    newlinks[hn][lt]=lu
	except ObjectDoesNotExist:
	    warning("Host %s doesn't exist in hostinfo" % host)
	    continue

    # Bulk updaters do all hosts with one invocation
    link_progs=getLinkPrograms(bulk=True)
    verbose("Getting bulk links")
    for link_prog in link_progs:
	linklist=getLinks(link_prog)
	for hn,lu,lt in linklist:
	    if hn not in newlinks:
		newlinks[hn]={}
	    newlinks[hn][lt]=lu

    updateLinks(hostlist, oldlinks, newlinks)

################################################################################
if __name__=="__main__":
    try:
    	opts,args=getopt.getopt(sys.argv[1:], "vhk")
    except getopt.GetoptError,err:
    	sys.stderr.write("Error: %s\n" % str(err))
    	usage()
	sys.exit(1)

    for o,a in opts:
    	if o=="-v":
	    verbFlag=True
    	if o=="-h":
	    usage()
	    sys.exit(0)
    	if o=="-k":
	    kiddingFlag=True

    main(args)

#EOF
