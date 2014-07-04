#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2014 Dougal Scott
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

# Script to replace a key:value pair with another value for all
# hosts or just a subset of hosts in the hostinfo database

import re
import sys
from host.models import checkKey
from host.models import HostinfoCommand, HostinfoException, KeyValue


###############################################################################
class Command(HostinfoCommand):
    description = 'Add alias to a host'

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            '-k', '--kidding',
            help="Don't actually do anything", action='store_true', default=False)
        parser.add_argument(
            '--all',
            help="Do for all hosts", action='store_true', default=False)
        parser.add_argument(
            'keyvalue',
            help='Name of the key/value pair to replace (key=value)', nargs=1)
        parser.add_argument(
            'newvalue',
            help='New value', nargs=1)
        parser.add_argument(
            'hosts',
            help="Hosts to replace the values on", nargs='*')

    ###########################################################################
    def handle(self, namespace):
        m = re.match("(?P<key>\w+)=(?P<value>.+)", namespace.keyvalue[0])
        if not m:
            raise HostinfoException("Must be in key=value format, not %s" % namespace.keyvalue[0])
        key = m.group('key').lower()
        value = m.group('value').lower()
        keyid = checkKey(key)
        if not namespace.hosts and not namespace.all:
            raise HostinfoException("Must specify a list of hosts or the --all flag")

        kvlist = KeyValue.objects.filter(keyid=keyid, value=value)
        for kv in kvlist:
            if (namespace.hosts and kv.hostid.hostname in namespace.hosts) or not namespace.hosts:
                if not namespace.kidding:
                    kv.value = namespace.newvalue[0]
                    kv.save()
                else:
                    sys.stderr.write("Would replace %s=%s with %s on %s\n" % (kv.keyid, kv.value, namespace.newvalue[0], kv.hostid))
        return None, 0

#EOF
