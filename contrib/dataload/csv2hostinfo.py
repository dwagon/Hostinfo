#!/usr/bin/env python
#
# Script to provide a generic conversion of a CSV formatted file to hostinfo commands
#
# Written by Dougal Scott <dwagon@pobox.com>
# $Id: csv2hostinfo.py 124 2012-12-05 21:17:22Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/contrib/dataload/csv2hostinfo.py $
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

import os, sys, getopt, csv, cStringIO, time
sys.path.append('/app/explorer/lib/python/site-packages')
from explorer.hostdet import getHardware
import rackmap

verbFlag=False
origin=sys.argv[0]

################################################################################
hostinfo={
    'site': {
    	'aka': ['site', 'location (site)', 'location'],
	},
    'rack': {
    	'aka': ['rack', 'rack/ru']
	},
    'hwdesc': {
    	'aka': ['item', 'hardware', 'hardware platform', 'model']
	},
    'domain': {
    	'aka': ['domain']
	},
    'hostname': {
    	'aka': ['item detail', 'hostname', 'host', 'server name', 'server', 'servername']
	},
    'asset': {
    	'aka': ['asset', 'asset tag', 'asset id']
	},
    'databases': {
    	'aka': ['database name'],
	},
    'serial': {
    	'aka': ['serial', 'serial number']
	},
    'buserver': {
    	'aka': ['backup up?', 'backup system']
	},
    'os': {
    	'aka': ['operating system', 'os', 'operatingsystem', 'os version']
	},
    'osrev': {
    	'aka': ['Revision', 
	'osver',
	#'os version'
	    ]
	},
    'type': {
    	'aka': ['type']
	},
    'service': {
    	'aka': ['environment', 'application']
	},
    'class': {
    	'aka': [
	    'class', 
	    #'status'
	    ]
	},
    'osrelease': {
    	'aka': ['operatingsystemservicepack', 'osrel', 'ops']
	},
    'dst_patched': {
    	'aka': ['tz test'],
	},
    }

################################################################################
#def convertOsrelease(str):
    #return str.replace(' ','_')

################################################################################
def convertOsrev(str):
    if str=='2003':
    	return 'server_2003'
    if str=='5.1':	# Handle excel changes
    	return '5.10'
    return str

################################################################################
def convertDst_Patched(str):
    if str=='0':
    	return 'tested'
    if str in ('x','X', '2'):
    	return 'failed_test'
    return None

################################################################################
def convertBuserver(str):
    for buserver in ['sunbak03', 'c1-ntx-back1p', 'lp-ntx-back01', 'mg-ntx-back01', 'c1-ntx-back2p']:
    	if buserver in str:
	    return buserver
    return str

################################################################################
def convertSite(str):
    sitemap={
    	'victoria gardens': '678victoria',
    	'vg': '678victoria',
    	'qv': '222lonsdale',
    	'surry hills': '268canterbury',
    	'melbourne central e.i.s': '360lonsdale',
    	'lp - liverpool st': '175liverpool',
    	'175 liverpool st': '175liverpool',
    	'sydney': '175liverpool',
    	'co-lo exhibition street': '300exhibition',
	'george st': '580george',
    	'300 exhibition st': '300exhibition',
    	'colo': '300exhibition',
    	'exhibition st': '300exhibition',
    	'dr site': '1822dandenong',
    	'clayton': '1822dandenong',
    	'150 lonsdale st': '150lonsdale',
    	'150 lonsdale': '150lonsdale',
    	'151 lonsdale': '150lonsdale',	# Doofus people
    	'152 lonsdale': '150lonsdale',	# Doofus people
	'8 govan': '8govan',
	'303 montague st': '303montague',
    	'brisbane': '151roma',
    	'perth': '100hay',
	'hobart': '70collins',
	'adelaide': '30pirie',
	}
    if str in sitemap:
    	return sitemap[str]
    if str in ('n/a'):
    	return None
    warning("Unhandled site: %s" % str)
    return str

################################################################################
def convertService(str):
    str=str.replace(' ','_')
    if str.startswith('ou='):
	str=str[3:]
    return str

################################################################################
def convertClass(str):
    if str=='ou=dev':
    	return 'dev'
    if str=='ou=prd':
    	return 'prod'
    for kl in ['dev', 'prod', 'staging', 'test']:
    	if kl in str:
	    return kl
    warning("Unhandled class: %s" % str)
    return str

################################################################################
def convertOs(str):
    if str=="-":
    	return ""
    if str in ['solaris', 'netware', 'aix', 'linux', 'windows']:
    	return str
    d={}
    if ' ' in str:
	d['os']=str.split(' ',1)[0]
	d['osrev']=str.split(' ',1)[1]
    if 'windows' in str:
    	d['os']='windows'
	d['osrev']=str
    return d

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
def getCSVfile(csvfile):
    f=open(csvfile)
    data=f.read()
    f.close()
    data=data.replace('\015', '\n')	# Handle excel CSV files
    strfd=cStringIO.StringIO(data)
    reader=csv.reader(strfd)
    return reader

################################################################################
def convertRack(value):
    if '/ru' in value:
    	value=value[:value.find('/ru')]
    if value in rackmap.rackmap:
    	return rackmap.rackmap[value]
    value=value.replace(' ','_')
    return value

################################################################################
def convertHwdesc(value):
    """ Keep the hardware description, but have the side effect of generating
    strings for hardware and type
    """
    hwtype,hwname=getHardware(value)
    d={}
    if hwname!='unknown':
    	d['hardware']=hwname
    if hwtype!='unknown':
    	d['type']=hwtype
    d['hwdesc']=value.replace(' ','_')
    return d

################################################################################
def analyseHeaders(line):
    """Work out from the header of the CSV file what all the columns mean
    """

    csvlist=[]
    for col in line:
    	found=False
    	col=col.lower()
	for key in hostinfo:
	    if col in hostinfo[key]['aka']:
	    	csvlist.append(key)
		found=True
		continue
	if not found:
	    csvlist.append('-')

    if verbFlag:
    	print "CSV to key mapping"
	for i in range(len(csvlist)):
	    try:
	    	line[i]
	    except IndexError:
	    	continue
	    if csvlist[i]=='-':
	    	print "\t%s-> unmapped" % line[i]
	    else:
		print "\t%s->%s" % (line[i], csvlist[i])

    return csvlist

################################################################################
def foundValue(key, value):
    """ If there is a function called convertKey where the Key is the name of the
    key, then call it to munge the value - otherwise do nothing to the value
    In both cases print out the hostinfo command to add the value
    """
    value=value.lower().strip()
    d={}
    try:
	handlerfn=globals()['convert%s' % key.title()]
	results=handlerfn(value)
	if type(results)==type({}):
	    d.update(results)
	elif type(results)==type(''):
	    d[key]=results
	elif type(results)==type(None):
	    pass
	else:
	    fatal("handler %s returned %s %s" % (handlerfn, type(results), results))
    except KeyError:
    	d[key]=value

    ans=[]
    for k,v in d.items():
	#ans.append((k,v.replace(' ','_')))
	ans.append((k,v))
    return ans
	
################################################################################
def runCmd(cmd):
    print cmd

################################################################################
def sanitiseHostname(hname):
    hname=hname.lower().strip()
    hname=hname.replace(' ','_')
    hname=hname.replace('(','')
    hname=hname.replace(')','')
    hname=hname.replace('.ext0','')
    hname=hname.replace('.ext1','')
    hname=hname.replace('.ext2','')
    hname=hname.replace('.ext3','')
    hname=hname.replace('.drx','')
    hname=hname.replace('.t3','')
    return hname

################################################################################
def analyseLine(line, csvlist, linecount):
    try:
	tmplist=csvlist[:]
	hostname=None
	ans=[]
	for bit in line:
	    if not tmplist:	# Someone has added extra fields in the data line
	    	break
	    curcol=tmplist.pop(0)
	    if curcol=='-':
		continue
	    if bit=='':
		continue
	    if curcol=='hostname':
		hostname=sanitiseHostname(bit)
	    else:
		if bit not in ('unknown', ''):
		    ans.extend(foundValue(curcol, bit))
	if hostname in ('', 'None', None):
	    warning("No hostname to use on line %d" % linecount)
	    return
	if hostname.startswith('????'):
	    warning("No good hostname to use on line %d - %s" % (linecount, hostname))
	    return
	if hostname not in hostinfo_cache:
	    runCmd("hostinfo_addhost --origin '%s' %s" % (origin,hostname))
	for key,value in ans:
	    update(hostname, key, value)
    except:
    	warning("Failed on line %d: %s" %  (linecount, line))
	raise

################################################################################
def update(host, key, value):
    if key not in keytypes:
	fatal("Key %s hasn't been created" % key)
    if host not in hostinfo_cache:
    	hostinfo_cache[host]={}
    if keytypes[key]=='list':
	updateList(host, key, value)
    else:
	updateVal(host, key, value)

###############################################################################
def updateVal(host, key, value):
    value='%s' % value  # Make it always a string
    if key not in hostinfo_cache[host]:
	runCmd("/app/hostinfo/bin/hostinfo_addvalue --origin='%s' %s='%s' %s" % (origin, key, value, host))
    elif value!=hostinfo_cache[host][key]:
	runCmd("/app/hostinfo/bin/hostinfo_addvalue --origin='%s' --update %s='%s' %s # Orig='%s'" % (origin, key, value, host, hostinfo_cache[host][key]))

###############################################################################
def updateList(host, key, value):
    # Get hivals to be a list of known existing vals for the host/key
    if type(value)!=type([]):
    	value=[value]
    if key not in hostinfo_cache[host]:
        hivals=[]
    else:
        if type(hostinfo_cache[host][key])==type([]):
            hivals=hostinfo_cache[host][key]
        else:
            hivals=[hostinfo_cache[host][key]]

    # Add vals to a list type if they aren't already there
    for v in value:
        if v not in hivals:
            runCmd("/app/hostinfo/bin/hostinfo_addvalue --origin='%s' --append %s='%s' %s" % (origin, key, v, host))

    # Remove vals from a list type if they are no longer there
    for v in hivals:
        if v not in value:
            runCmd("/app/hostinfo/bin/hostinfo_deletevalue %s='%s' %s" % (key, v, host))

################################################################################
def loadHostinfoKeys():
    keytype={}
    f=os.popen('/app/hostinfo/bin/hostinfo_showkey')
    for line in f:
	bits=line.strip().split()
	keytype[bits[0]]=bits[1]
    f.close()
    return keytype

################################################################################
def loadAllHostinfo():
    """ Load all the data from hostinfo so we don't spend wasted time updating values with the
    same value
    """
    hidata={}
    str=""
    keytypes=loadHostinfoKeys()
    keylist=sorted(hostinfo.keys())
    keylist.remove('hostname')
    for k in keylist:
    	str+=" -p %s " % k
    f=os.popen('/app/hostinfo/bin/hostinfo --noheader --csv %s' % str)
    data=f.read()
    f.close()
    strfd=cStringIO.StringIO(data)
    reader=csv.reader(strfd)

    for line in reader:
    	host=line.pop(0)
	hidata[host]={}
	for key in keylist:
	    data=line.pop(0)
	    if not data:
	    	continue
	    if keytypes[key]=='list':
		hidata[host][key]=data.split(',')
	    else:
		hidata[host][key]=data

    return hidata,keytypes

################################################################################
def main(csvfile):
    global hostinfo_cache, keytypes
    hostinfo_cache,keytypes=loadAllHostinfo()
    f=getCSVfile(csvfile)
    linecount=-1
    for line in f:
    	linecount+=1
    	if linecount==0:
	    csvlist=analyseHeaders(line)
    	else:
	    analyseLine(line, csvlist, linecount)

################################################################################
if __name__=="__main__":
    try:
    	opts,args=getopt.getopt(sys.argv[1:], "v", ["origin="])
    except getopt.GetoptError,err:
    	sys.stderr.write("Error: %s\n" % str(err))
    	usage()
	sys.exit(1)

    for o,a in opts:
    	if o=="-v":
	    verbFlag=True
    	if o=="--origin":
	    origin=a
    origin+=" %s" % time.strftime('%Y-%m-%d')

    main(args[0])

#EOF
