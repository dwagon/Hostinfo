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

# Script to show the history of an host
# Unfortunately due to the way foreignkeys work all audits details about a host's
# keys are deleted with the host

from django.core.exceptions import ObjectDoesNotExist
from host.models import AllowedKey, getHost, KeyValue
from host.models import HostinfoCommand


###############################################################################
class Command(HostinfoCommand):
    description = 'Add alias to a host'
    _keycache = {}

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            '-o', '--origin',
            help='Show the origin of the change', action='store_true',
            dest='originFlag')
        parser.add_argument(
            '-a', '--actor',
            help='Show the actor of the change', action='store_true',
            dest='actorFlag')
        parser.add_argument('host', help='Host to show the history of')

    ###########################################################################
    def handle(self, namespace):
        outstr = ""
        host = getHost(namespace.host)
        if not host:
            return outstr, 1
        kvchanges = KeyValue.history.filter(hostid_id=host.id).order_by('history_date')
        for kv in kvchanges:
            key = self.getKeyName(kv.keyid_id)
            if kv.history_type == '+':
                msg = "added %s:%s with %s on %s" % (host.hostname, key, kv.value, kv.history_date)
            elif kv.history_type == '-':
                msg = "deleted %s:%s on %s" % (host.hostname, key, kv.history_date)
            elif kv.history_type == '~':
                msg = "changed %s:%s to %s on %s" % (host.hostname, key, kv.value, kv.history_date)
            if namespace.originFlag:
                msg = "%s %s" % (msg, kv.origin)
            outstr += "%s\n" % msg
        return outstr, 0

    ###########################################################################
    def getKeyName(self, keyid):
        if keyid in self._keycache:
            return self._keycache[keyid]
        try:
            key = AllowedKey.objects.get(id=keyid).key
        except ObjectDoesNotExist:
            key = "<deleted>"
        self._keycache[keyid] = key
        return key

# EOF
