#!/usr/bin/env python
# 
# Script to validate the contents of keys
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: hostinfo_validatekey.py 126 2012-12-05 21:19:03Z dougal.scott@gmail.com $
# $HeadURL: svn+ssh://localhost/Library/Subversion/Repository/hostinfo/trunk/reports/hostinfo_validatekey.py $
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

import os, sys, getopt

verbFlag=False

################################################################################
def verbose(msg):
    if verbFlag:
    	sys.stderr.write("%s\n" % msg)

################################################################################
def usage():
    sys.stderr.write("Usage: %s\n" % sys.argv[0])

################################################################################
def getRestrictedKeys():
    return getKeyList('RESTRICTED')

################################################################################
def getSingleKeys():
    return getKeyList('single')

################################################################################
def getKeyList(str):
    keys=[]
    f=os.popen('hostinfo_showkey')
    for line in f:
    	if str in line:
	    keys.append(line.split()[0])
    f.close()
    return keys

################################################################################
def getRestrictedValues(key):
    tmp=[]
    f=os.popen('hostinfo_listrestrictedvalue %s' % key)
    for line in f:
    	tmp.append(line.strip())
    f.close()
    return tmp

################################################################################
def validateRestricted():
    keys=getRestrictedKeys()
    for key in keys:
    	verbose("Checking restricted key %s" % key)
    	vals=getRestrictedValues(key)
	f=os.popen('hostinfo -p %s %s.defined' % (key,key))
	for line in f:
	    host=line.split()[0]
	    val=line.strip().split()[-1].replace('%s=' % key,'')
	    if val not in vals:
	    	print "Host %s has %s=%s not %s" % (host, key, val, ", ".join(vals))

################################################################################
def validateSingle():
    keys=getSingleKeys()
    for key in keys:
    	verbose("Checking single key %s" % key)
	f=os.popen('hostinfo -p %s %s.defined' % (key,key))
	for line in f:
	    if ',' in line:
	    	print line.strip()

################################################################################
def main():
    # All values of a restricted value key should be in the list of restricted values
    validateRestricted()
    # There should only be one value for single keys
    #validateSingle()

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

    main()

#EOF
