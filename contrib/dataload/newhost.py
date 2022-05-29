#!/usr/bin/env python
# 
# Script to prompt for the details of a new host
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: newhost.py 124 2012-12-05 21:17:22Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/contrib/dataload/newhost.py $
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

import os, sys, getopt

verbFlag=False
origin=os.getlogin() 
cmdlist=[]

################################################################################
def verbose(msg):
    if verbFlag:
    	sys.stderr.write("%s\n" % msg)

################################################################################
def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)

################################################################################
def usage():
    sys.stderr.write("Usage: %s\n" % sys.argv[0])

################################################################################
def runCmd(cmd):
    cmdlist.append(cmd)
#    if flags['kidding']:
#    	sys.stdout.write("%s\n" % cmd)
#    else:
#    	f=os.popen(cmd)
#	for line in f:
#	    warning(line.strip())
#	f.close()

################################################################################
def ask(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    ans=sys.stdin.readline().strip()
    return ans

################################################################################
def getHost(host):
    if not host:
	host=ask("Hostname? ")
    runCmd("hostinfo_addhost --origin=%s %s" % (origin, host))
    return host

################################################################################
def getGeneric(host, key, question=''):
    if not question:
    	question="%s? " % key.title()
    val=ask(question)
    if val:
    	runCmd("hostinfo_addvalue --origin=%s %s=%s %s" % (origin, key, val, host))
    return val

################################################################################
def checkHost(host):
    f=os.popen("/app/hostinfo/bin/hostinfo %s" % host)
    x=f.close()
    if x:
	return False
    else:
    	print "#" * 80
    	print "# Host %s already exists" % host
    	return True

################################################################################
def checkSerial(serial):
    f=os.popen("/app/hostinfo/bin/hostinfo serial=%s" % serial)
    output=f.readlines()
    x=f.close()
    if x:
    	return False
    else:
    	print "#" * 80
    	print "# Hosts matched serial %s" % serial
    	for line in output:
	    print "# %s " % line.strip()
    	print "#" * 80

################################################################################
def main(host=''):
    host=getHost(host)
    hware=getGeneric(host, "hardware")
    getGeneric(host, "site")
    getGeneric(host, "rack")
    asset=getGeneric(host, "asset")
    serial=getGeneric(host, "serial")

    if hware.startswith('sun') or hware.startswith('ibm'):
    	runCmd("hostinfo_addvalue --origin=%s type=server %s" % (origin,host))
	if host.endswith('p'):
	    runCmd("hostinfo_addvalue --origin=%s class=prod %s" % (origin,host))
	elif host.endswith('s'):
	    runCmd("hostinfo_addvalue --origin=%s class=staging %s" % (origin,host))
	elif host.endswith('t'):
	    runCmd("hostinfo_addvalue --origin=%s class=test %s" % (origin,host))
	elif host.endswith('d'):
	    runCmd("hostinfo_addvalue --origin=%s class=dev %s" % (origin,host))
	else:
	    getGeneric(host, "class")
    else:
	getGeneric(host, "type")
	getGeneric(host, "class")

    checkHost(host)
    checkSerial(serial)
    #checkAsset(asset)

    for cmd in cmdlist:
    	print cmd

################################################################################
if __name__=="__main__":
    global flags
    flags={'kidding': False}
    try:
    	opts,args=getopt.getopt(sys.argv[1:], "vhk",["origin="])
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
    	if o=="--origin":
	    origin="'%s'" % a
    	if o=="-k":
	    flags['kidding']=True

    if args:
    	host=args[0]
    else:
    	host=''

    main(host)

#EOF
