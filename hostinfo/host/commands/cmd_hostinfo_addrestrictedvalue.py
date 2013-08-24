#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
# $Id: models.py 101 2012-06-23 11:09:39Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/hostinfo/hostinfo/models.py $
#
#    Copyright (C) 2012 Dougal Scott
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
import re
from hostinfo.host.models import AllowedKey, RestrictedValue, HostinfoException
from hostinfo.host.models import HostinfoCommand

class Command(HostinfoCommand):
    description='Add a new allowable value to a restricted key'

    ############################################################################
    def parseArgs(self, parser):
        parser.add_argument('keyvalue',help='Name of the key/value pair to allow (key=value)')

    ############################################################################
    def handle(self, namespace):
        m=re.match("(?P<key>\w+)=(?P<value>.+)", namespace.keyvalue)
        if not m:
            raise HostinfoException("Must be specified in key=value format")
        key=m.group('key').lower()
        value=m.group('value').lower()
        keyobjlist=AllowedKey.objects.filter(key=key)
        if len(keyobjlist)!=1:
            raise HostinfoException("No key %s found" % key)
        keyobj=keyobjlist[0]
        if not keyobj.restrictedFlag:
            raise HostinfoException("Key %s isn't a restrictedvalue key" % key)
        rvallist=RestrictedValue.objects.filter(keyid=keyobj, value=value)
        if rvallist:
            raise HostinfoException("Already a key %s=%s in the restrictedvalue list" % (key, value))
        rv=RestrictedValue(keyid=keyobj, value=value)
        rv.save()
        return None,0

#EOF
