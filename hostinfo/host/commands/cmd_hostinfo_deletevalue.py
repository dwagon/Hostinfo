#
# Written by Dougal Scott <dougal.scott@gmail.com>
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
from host.models import checkKey, HostinfoException, KeyValue
from host.models import HostinfoCommand, getHost, ReadonlyValueException

class Command(HostinfoCommand):
    description='Delete an alias from a host'

    ############################################################################
    def parseArgs(self, parser):
        parser.add_argument('keyvalue',help='The key or keyvalue to delete (key[=value])')
        parser.add_argument('--readonlyupdate',help='Write to a readonly key', action='store_true')
        parser.add_argument('host',help='The host(s) to delete the value from', nargs='+')

    ############################################################################
    def handle(self, namespace):
        m=re.match("(?P<key>\w+)=(?P<value>.+)", namespace.keyvalue)
        if m:
            key=m.group('key').lower()
            value=m.group('value').lower()
        else:
            key=namespace.keyvalue.lower()
            value=''
        keyid=checkKey(key)
        for host in namespace.host:
            hostid=getHost(host)
            if not hostid:
                raise HostinfoException("Unknown host: %s" % host)
            if value:
                kvlist=KeyValue.objects.filter(hostid=hostid, keyid=keyid, value=value)
            else:
                kvlist=KeyValue.objects.filter(hostid=hostid, keyid=keyid)
            if not kvlist:
                raise HostinfoException("Host %s doesn't have key %s" % (host, key))
            else:
                for kv in kvlist:
                    try:
                        kv.delete(readonlychange=namespace.readonlyupdate)
                    except ReadonlyValueException:
                        raise HostinfoException("Cannot delete a readonly value")
        return None,0

#EOF
