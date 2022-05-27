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

from host.models import getHost, getOrigin, Host
from host.models import HostinfoCommand, HostinfoException


###############################################################################
class Command(HostinfoCommand):
    description = "Add a new host"

    ############################################################################
    def parseArgs(self, parser):
        parser.add_argument("host", help="The host to add", nargs="+")
        parser.add_argument("--origin", help="The origin of this host")

    ############################################################################
    def handle(self, namespace):
        origin = getOrigin(namespace.origin)
        for host in namespace.host:
            host = host.lower()
            if self.checkHost(host):
                raise HostinfoException("Host %s already exists" % host)
            if host[0] in ("-",):
                raise HostinfoException(
                    "Host begins with a forbidden character ('%s') - not adding"
                    % host[0]
                )
            hobj = Host(hostname=host, origin=origin)
            hobj.save()
        return None, 0

    ############################################################################
    def checkHost(self, host):
        h = getHost(host)
        if h:
            return True
        return False


# EOF
