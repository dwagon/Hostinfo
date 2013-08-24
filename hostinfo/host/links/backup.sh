#/bin/sh
# Hostinfo link script for nwreporter 
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: backup.sh 6 2010-01-12 07:41:47Z dwagon $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/hostinfo/hostinfo/links/backup.sh $

host=$1

butmp=`/app/hostinfo/bin/hostinfo -p buserver buserver.defined ${host}`
if [ "$?" = "0" ]; then
    buserver=`echo ${butmp} | sed 's/.*buserver=//'`
    pth=/app/nwreporter/data/${buserver}/clients/${host}.*html
else
    pth=/app/nwreporter/data/*/clients/${host}.*html
fi

if [ -f ${pth} ]; then
    url=`echo ${pth} | sed 's/\/app/http:\/\/opscmdb/'`
    echo "${url} Backup Report"
    exit 0
else
    exit 1
fi

#EOF
