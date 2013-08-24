#!/usr/local/bin/python
# 
# Script to ping every host and update the 'lastping' key
# to give an indication of 'liveness'
#
# Writen by Dougal Scott <dwagon@pobox.com>
# $Id: pingCheck.py 80 2011-02-15 11:13:29Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/contrib/auto_updaters/pingCheck.py $

import os, time

############################################################################
def pingCheck(hostname):
    f=os.popen('/usr/sbin/ping %s 2>/dev/null' % hostname)
    rc=f.close()
    if not rc:
	return True
    return False

################################################################################
def getHostlist(hostargs=''):
    tmp=[]
    f=os.popen('hostinfo %s' % hostargs)
    for line in f:
    	hostname=line.strip()
	tmp.append(Host(hostname))
    f.close()
    return tmp

################################################################################
def main(hostargs=''):
    print "origin=pingCheck"
    today=time.strftime('%Y-%m-%d')
    hostlist=getHostlist(hostargs)
    for host in hostlist:
	if pingCheck(host):
	    print "%s lastping=%s" % (hostname, today)

################################################################################
if __name__=="__main__":
    main()

#EOF
