#!/usr/bin/env python
#
# Script to create a wiki page per host in hostinfo
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: wikiImport.py 124 2012-12-05 21:17:22Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/contrib/dataload/wikiImport.py $
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

import os, sys, getopt, re

verbFlag=False
kiddingFlag=False
template="/Users/dwagon/Documents/src/hostinfo/trunk/contrib/dataload/wikiImport.template"
tmp="/tmp"
user="<USER>"	# User (robot?) who will add the pages
user="dwagon"	# User (robot?) who will add the pages
wikiInstallPath='/app/wiki/current'	# Path to installation directory of wiki - $IP
wikiInstallPath='/Users/dwagon/Sites'	# Path to installation directory of wiki - $IP
importer="maintenance/importTextFile.php"
dumper="maintenance/dumpBackup.php"
nuker="maintenance/deleteBatch.php"

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
    sys.stderr.write("Usage: %s [host,...]\n" % sys.argv[0])

################################################################################
def createAliasPage(host, title, alias):
    verbose("Creating alias %s -> %s" % (alias, host))
    tmpfile=os.path.join(tmp,"%s.wiki" % alias)
    f=open(tmpfile,'w')
    f.write("#REDIRECT [[Host:%s]]\n" % host)
    f.close()

    importPage(tmpfile, title)

    os.unlink(tmpfile)

################################################################################
def createHostPage(host, title, hosttype, templatedata):
    verbose("Creating host %s" % host)
    tmpfile=os.path.join(tmp,"%s.wiki" % host)

    contents=templatedata.replace('%HOSTNAME%',host)

    # Create a tmp file with the contents from the template
    f=open(tmpfile,'w')
    f.write(contents)
    f.close()

    importPage(tmpfile, title)

    os.unlink(tmpfile)

################################################################################
def importPage(tmpfile, title):
    # Import article into the wiki
    cmd="php %s/%s --nooverwrite --title %s --user %s %s" % (wikiInstallPath, importer, title, user, tmpfile)
    if kiddingFlag:
    	warning("%s" % cmd)
    else:
	g=os.popen(cmd)
	for line in g:
	    verbose(line.strip())
	g.close()

################################################################################
def loadExistingWiki():
    """ Dump the existing wiki in xml and do a very basic extraction of the list of pages
    Note that this is mostly XML ignorant and won't survive a change in schema
    """
    pages=[]
    reg=re.compile('<title>(?P<title>.*)</title>')
    g=os.popen("sudo php %s/%s --quiet --current" % (wikiInstallPath, dumper))
    for line in g:
    	if '<title>' in line:
	    m=reg.search(line)
	    if m:
	    	pages.append(m.group('title'))
	    else:
	    	warning("Unknown title line: %s" % line.strip())
    return pages
    	
################################################################################
def getHostType(host):
    f=os.popen('hostinfo -p type %s' % host)
    output=f.readline().strip()
    f.close()
    hosttype=output.split()[-1].replace('type=','')
    return hosttype

################################################################################
def getAliases():
    aliases={}
    f=os.popen('hostinfo_listalias --all')
    for line in f:
    	line=line.strip()
	alias,host=line.split()
	if host not in aliases:
	    aliases[host]=[]
	aliases[host].append(alias)
    f.close()
    return aliases

################################################################################
def deletePages(hostlist):
    hostfile='/tmp/delete_Pages'
    verbose("Deleting %d pages" % (len(hostlist)))
    f=open(hostfile,'w')
    for host in hostlist:
    	f.write("Host:%s\n" % host)
    f.close()
    g=os.popen("sudo php %s/%s -i 1 -u %s %s" % (wikiInstallPath, nuker, user, hostfile))
    output=g.read()
    x=g.close()
    if x:
    	warning(output)

################################################################################
def main(hostlist, flags):
    pagelist=loadExistingWiki()
    templatedata=open(template).read()
    aliases=getAliases()
    for host in hostlist:
	title="Host:%s" % host
	if title in pagelist or title.replace('_',' ').strip() in pagelist:
	    pass
	else:
	    hosttype=getHostType(host)
	    createHostPage(host, title, hosttype, templatedata)

	if host in aliases:
	    for alias in aliases[host]:
	    	title="Host:%s" % alias
		if title not in pagelist:
		    createAliasPage(host, title, alias)

    if flags['fullFlag']:
    	hostpages=[page.replace('Host:','').replace(' ','_') for page in pagelist if page.startswith('Host:')]
	for host in hostlist:
	    if host in hostpages:
		hostpages.remove(host)

	for host in aliases:
	    for alias in aliases[host]:
	    	if alias in hostpages:
		    hostpages.remove(alias)

	if hostpages:
	    print "Remaining host pages are %s" % " ".join(hostpages)
	    if flags['nukeFlag']:
		deletePages(hostpages)

################################################################################
if __name__=="__main__":
    flags={'fullFlag': False, 'nukeFlag': False }
    try:
    	opts,args=getopt.getopt(sys.argv[1:], "vhk", ["template=", "tmp=", "user=", "importer=","nuke"])
    except getopt.GetoptError,err:
    	sys.stderr.write("Error: %s\n" % str(err))
    	usage()
	sys.exit(1)

    for o,a in opts:
    	if o=="-v":
	    verbFlag=True
    	if o=="-k":
	    kiddingFlag=True
    	if o=="-h":
	    usage()
	    sys.exit(0)
	if o=="--template":
	    template=a
	if o=="--tmp":
	    tmp=a
	if o=="--user":
	    user=a
	if o=="--importer":
	    importer=a
	if o=="--nuke":
	    flags['nukeFlag']=True

    if args:
    	hostlist=args[:]
	flags['fullFlag']=False
    else:
    	hostlist=[line.strip() for line in os.popen('hostinfo')]
	flags['fullFlag']=True

    main(hostlist, flags)

#EOF
