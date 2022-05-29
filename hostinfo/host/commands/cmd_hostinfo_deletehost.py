#
# Written by Dougal Scott <dougal.scott@gmail.com>
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

from host.models import KeyValue, HostAlias, getHost
from host.models import HostinfoCommand, HostinfoException


###############################################################################
class Command(HostinfoCommand):
    description = "Delete a host"

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            "--lethal", help="Actually do the delete - NO UNDO", action="store_true"
        )
        parser.add_argument("host", help="Name of host to delete")

    ###########################################################################
    def handle(self, namespace):
        host = namespace.host.lower()
        h = getHost(host)
        if not h:
            raise HostinfoException("Host %s doesn't exist" % host)

        if not namespace.lethal:
            raise HostinfoException("Didn't do delete as no --lethal specified")

        # Delete aliases
        aliases = HostAlias.objects.filter(hostid=h.id)
        for alias in aliases:
            if namespace.lethal:
                alias.delete()

        # Delete key/values
        kvs = KeyValue.objects.filter(hostid=h.id)
        for kv in kvs:
            if namespace.lethal:
                kv.delete(readonlychange=True)

        # Delete the host
        if namespace.lethal:
            h.delete()
        return None, 0


# EOF
