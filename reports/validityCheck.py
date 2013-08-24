#!/usr/bin/env python
# 
# Script to check the validity of the hostinfo database as much as it can
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: validityCheck.py 126 2012-12-05 21:19:03Z dougal.scott@gmail.com $
# $HeadURL: svn+ssh://localhost/Library/Subversion/Repository/hostinfo/trunk/reports/validityCheck.py $
#
#    Copyright (C) 2008 Dougal Scott
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

import os, sys, getopt, csv, datetime
sys.path.append('/app/explorer/lib/python/site-packages')
import rackmap
sys.path.append('/app/interactive/lib/python/site-packages')
import hardware

verbFlag=False
_racklist=None

################################################################################
def verbose(msg):
    if verbFlag:
    	sys.stderr.write("%s\n" % msg)

################################################################################
def usage():
    sys.stderr.write("Usage: %s\n" % sys.argv[0])

################################################################################
def loadKeyTypes():
    keys={}
    f=os.popen('hostinfo_showkey')
    for line in f:
    	bits=line.split()
	keys[bits[0]]=bits[1]
    f.close()
    return keys
    	
################################################################################
def loadHostinfo():
    results={}
    keytypes=loadKeyTypes()
    listkeys=[k for k in keytypes if keytypes[k]=='list']
    f=os.popen('hostinfo --csv --showall')
    headerline=f.readline().strip()
    bitnames=headerline.split(',')
    reader=csv.reader(f)
    for line in reader:
    	host=line[0]
	results[host]={}
    	for bit in bitnames:
	    bitindex=bitnames.index(bit)
	    data=line[bitindex].strip()
	    if data=='':
	    	results[host][bit]=None
		continue
	    if bit in listkeys:
		results[host][bit]=data.split(',')
	    else:
		results[host][bit]=data
    return results

################################################################################
def virtualCheck(host):
    """ A real check but of virtual hosts 
    """

    if not hostinfo[host]['virtualmaster']:
    	whinge("VM %s: no virtualmaster defined" % host)
    else:
    	vm=hostinfo[host]['virtualmaster']
	if vm not in hostinfo:
	    whinge("VM %s: has virtualmaster %s not in hostinfo" % (host, vm), 'hostinfo_deletevalue virtualmaster=%s %s' % (hostinfo[host]['virtualmaster'], host))
	else:
	    if not hostinfo[vm]['virtuals']:
	    	whinge( "VM %s: master %s has no virtuals " % (host, vm), 'hostinfo_addvalue virtuals=%s %s' % (host, vm))
	    elif host not in hostinfo[vm]['virtuals']:
	    	if explored(vm):
		    vmstr=" (Explored)"
		else:
		    vmstr=""
	    	whinge("VM %s: is not in master %s's%s list of virtuals: %s" % (host, vm, vmstr, ", ".join(hostinfo[vm]['virtuals'])), 'hostinfo_addvalue --append virtuals=%s %s' % (host, vm))

    for key in ('site', 'rack', 'hardware', 'hwdesc', 'virtuals'):
	if hostinfo[host][key]:
	    whinge("VM %s: has %s defined [=%s]" % (host, key, hostinfo[host][key]), 'hostinfo_deletevalue %s=%s %s' % (key, hostinfo[host][key], host))

################################################################################
def nonVirtualCheck(host):
    """ Check for things that should only be set on a virtual """
    for key in ['virtualmaster', 'vmtype', 'zonename']:
	if hostinfo[host][key]:
	    whinge("Host %s: has %s defined [=%s]" % (host, key, hostinfo[host][key]), 'hostinfo_deletevalue %s=%s %s' % (key, hostinfo[host][key], host))

    if hostinfo[host]['virtuals']:
    	for vm in hostinfo[host]['virtuals']:
	    if vm not in hostinfo:
	    	whinge("Host %s: Virtual %s doesn't exist" % (host, vm), 'hostinfo_deletevalue virtuals=%s %s' % (vm, host))
	    	continue
	    if hostinfo[vm]['virtualmaster']!=host:
	    	whinge("Host %s: Virtual %s's virtualmaster points to %s" % (host, vm, hostinfo[vm]['virtualmaster']))

################################################################################
def diskCheck(host):
    """ Check disk arrays"""
    if not hostinfo[host]['attachedto']:
    	whinge("Disk %s isn't attached to anything" % host)
    else:
    	at=hostinfo[host]['attachedto']
	if at not in hostinfo:
	    whinge("Disk %s is attached to a host that doesn't exist: %s" % (host, at), 'hostinfo_deletevalue attachedto=%s %s' % (hostinfo[host]['attachedto'], host))

################################################################################
def hardwareCheck(host):
    """ Check things based on the hardware """

    if hostinfo[host]['hardware'] and not hostinfo[host]['hwdesc']:
    	whinge("Host %s has a hardware of %s but no hwdesc defined" % (host, hostinfo[host]['hardware']), "hostinfo_addvalue hwdesc=%s %s" % (hostinfo[host]['hardware'], host))

    if hostinfo[host]['hwdesc']:
    	testtype, testhardware=hardware.getHardware(hostinfo[host]['hwdesc'])

	if testtype=='unknown':
	    return

	if not hostinfo[host]['hardware']:
	    whinge("Host %s has a hwdesc of %s but no hardware defined" % (host, hostinfo[host]['hwdesc']), "hostinfo_addvalue hardware=%s %s" % (testhardware, host))

	if hostinfo[host]['hardware']!=testhardware:
	    whinge("Host %s has a hardware of %s but should be %s based on hwdesc of %s" % (host, hostinfo[host]['hardware'], testhardware, hostinfo[host]['hwdesc']), "hostinfo_addvalue --update hardware=%s %s" % (testhardware, host))

	if hostinfo[host]['type']!=testtype:
	    whinge("Host %s has a type of %s but should be %s based on hwdesc of %s" % (host, hostinfo[host]['type'], testtype, hostinfo[host]['hwdesc']), "hostinfo_addvalue --update type=%s %s" % (testtype, host))

################################################################################
def whinge(complaint, cmd=""):
    global buff
    if cmd:
	buff+="%s\t# %s" % (cmd, complaint)
    else:
	buff+="# %s" % complaint

################################################################################
def locationCheck(host):
    """ Check things based on the location """
    global _racklist
    if not _racklist:
    	_racklist=rackmap.rackmap.values()

    if hostinfo[host]['rack'] and not hostinfo[host]['site']:
    	whinge("Host %s: rack of %s but no site defined" % (host, hostinfo[host]['rack']))

    if hostinfo[host]['rack'] and hostinfo[host]['rack'] not in _racklist:
    	whinge("Host %s: in an unknown rack '%s'" % (host, hostinfo[host]['rack']))
	
################################################################################
def networkCheck(host):
    if hostinfo[host]['ipsanhosts']:
    	if hostinfo[host]['type']!='router':
	    whinge("Switch %s: not of type router [%s]" % (host, hostinfo[host]['type']), "hostinfo_addvalue --update type=router %s" % host)

	for h in hostinfo[host]['ipsanhosts']:
	    if h not in hostinfo:
		whinge("Switch %s: %s in ipsanhosts but doesn't exist" % (host, h), "hostinfo_deletevalue ipsanhosts=%s %s" % (h, host))
		continue
	    if not hostinfo[h]['ipsanswitch']:
	    	whinge("Switch %s: Host %s doesn't have ipsanswitch set correctly [%s]" % (host, h, hostinfo[h]['ipsanswitch']),"hostinfo_addvalue --update ipsanswitch=%s %s" % (host, h)) 
  	
################################################################################
def hostCheck(host):
    if hostinfo[host]['ipsanswitch']:
    	sw=hostinfo[host]['ipsanswitch']
	if host not in hostinfo[sw]['ipsanhosts']:
	    whinge("Host %s: Switch %s doesn't know about this host" % (host, sw), "hostinfo_addvalue --append ipsanhosts=%s %s" % (host, sw))
    	
################################################################################
def explored(host):
    """ Return true if the host has had an explorer run recently
    This means that various fields can be trusted more
    """
    if not hostinfo[host]['explorerdate']:
    	return False
    bits=hostinfo[host]['explorerdate'].split('-')
    expdate=datetime.date(year=int(bits[0]), month=int(bits[1]), day=int(bits[2]))
    today=datetime.date.today()
    age=today-expdate
    if age.days<60:
	return True
    return False

################################################################################
def main(hostlist=None):
    global hostinfo
    global buff
    hostinfo=loadHostinfo()
    if not hostlist:
    	hostlist=hostinfo.keys()
    for host in hostlist:
    	buff=""
    	verbose("Validating %s" % host)
    	if hostinfo[host]['type']=='virtual':
	    virtualCheck(host)
	else:
	    nonVirtualCheck(host)
	if hostinfo[host]['type']=='disk':
	    diskCheck(host)
	hardwareCheck(host)
	locationCheck(host)
	networkCheck(host)
	hostCheck(host)
	if buff:
	    print
	    if explored(host):
		str="(Explored)"
	    else:
		str=""
	    print "# %s %s" % (host, str)
	    print buff

################################################################################
if __name__=="__main__":
    try:
    	opts,args=getopt.getopt(sys.argv[1:], "vh")
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

    main(args)

#EOF
