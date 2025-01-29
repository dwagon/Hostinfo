#!/usr/bin/env python
# 
# Script to create a generic report on hostinfo keys
# Should record the number of records, the percentage of keys defined, the top values defined
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: genericReport.py 126 2012-12-05 21:19:03Z dougal.scott@gmail.com $
# $HeadURL: svn+ssh://localhost/Library/Subversion/Repository/hostinfo/trunk/reports/genericReport.py $
#
#    Copyright (C) 2025 Dougal Scott
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

verbFlag=False
numvals=10
outfile=None
datestampFlag=True

reportname = "generic report"
reportdesc = "Report on stuff"

################################################################################
def Verbose(msg):
    if verbFlag:
    	sys.stderr.write("%s\n" % msg)

################################################################################
def usage():
    sys.stderr.write("Usage: %s\n" % sys.argv[0])
    sys.stderr.write("   [--numvals=<int>]\tNumber of vals to print for each key (default %d)\n" % numvals)
    sys.stderr.write("   [--outfile=<file>]\tWhere to put the output. Default stdout\n")
    sys.stderr.write("   [--nodatestamp]\tDon't datestamp the output file\n")

################################################################################
def getKeys():
    keylist=[]
    f=os.popen('hostinfo_showkey')
    for line in f:
    	keylist.append(line.strip().split()[0])
    f.close()
    return keylist
    	
################################################################################
def output(str):
    if outfile:
    	if datestampFlag:
	    datestr=time.strftime('%Y%m%d')
	    filename='%s_%s' % (outfile, datestr)
    	f=open(filename,'a')
	f.write("%s\n" % str)
	f.close()
    else:
    	print str

################################################################################
def countDict(d):
    """ Return a list of the top 'numvals' values in the dictionary d
    """
    l=[]
    for k,v in d.items():
	l.append((v,k))
    l.sort()
    l.reverse()
    return  list(l[:numvals])

################################################################################
def getStats(key, numrecords):
    """ Get the basic statistics for the key
    """
    count=0
    d={}
    f=os.popen('hostinfo -p %s %s.defined' % (key,key))
    for line in f:
    	count+=1
	val=line[line.find('=')+1:].strip()
	d[val]=d.get(val,0)+1
    f.close()
    ans=countDict(d)
    output("%s:%d:%d:%s" % (key, count, numrecords-count, ans))

################################################################################
def getRecordCount():
    count=0
    f=os.popen('hostinfo')
    for line in f:
    	count+=1
    f.close()
    return count

################################################################################
def main():
    keylist=getKeys()
    numrecords=getRecordCount()
    for key in keylist:
    	getStats(key, numrecords)

################################################################################
if __name__=="__main__":
    try:
    	opts,args=getopt.getopt(sys.argv[1:], "vh",["numvals=", "outfile=", "nodatestamp"])
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
	if o=="--numvals":
	    numvals=int(a)
	if o=="--outfile":
	    outfile=a
	if o=="--nodatestamp":
	    datestampFlag=False

    main()

#EOF
