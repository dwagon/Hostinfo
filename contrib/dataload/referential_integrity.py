#!/usr/bin/python
# 
# Script to
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: referential_integrity.py 124 2012-12-05 21:17:22Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/contrib/dataload/referential_integrity.py $
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

################################################################################
def Verbose(msg):
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
def loadData(key):
    data={}
    f=os.popen("/app/hostinfo/bin/hostinfo --csv --noheader -p %s %s.defined" % (key, key))
    for line in f:
    	bits=line.strip().split(',',1)
	host=bits[0]
	listofvals=bits[1][1:-1]
	data[host]=listofvals.split(',')
    return data

################################################################################
def runCmd(cmd):
    sys.stderr.write("%s\n" % cmd)

################################################################################
def checkIntegrity(children, parent):
    parentsdata=loadData(parent)
    childsdata=loadData(children)
    # For every child there should be:
    #     a parent defined
    #     a entry for itself in the parent
    # Remember that parent servers contain child data and vice versa
    for dad in parentsdata:
    	print
    	print "parent=%s children=%s" % (dad, parentsdata[dad])
	for kid in parentsdata[dad]:
	    print "    child=%s" % kid
	    if kid not in childsdata:
	    	warning("Parent %s has phantom child %s" % (dad,kid))
		runCmd("/app/hostinfo/bin/hostinfo_deletevalue %s=%s %s" % (parent, kid, dad))
		continue
	    print "    childsdata=%s" % childsdata[kid]
	    if childsdata[kid]!=[dad]:
	    	fatal("Child %s doesn't know that its parent is %s" % (kid, dad))

    for	kid in childsdata:
    	print
	print "child=%s parent=%s" % (kid, childsdata[kid])
	for dad in childsdata[kid]:
	    print "    dad=%s" % dad
	    print "    dad's children=%s" % parentsdata[dad]
	    if kid not in parentsdata[dad]:
	    	warning("Parent %s doesn't know about child %s" % (dad,kid))
		runCmd("/app/hostinfo/bin/hostinfo_addvalue --append %s=%s %s" % (parent, kid, dad))

################################################################################
def main():
    pairs=[('zones','zonemaster'), ('blades', 'bladeenclosure')]
    for parent,children in pairs:
	checkIntegrity(children, parent)

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
