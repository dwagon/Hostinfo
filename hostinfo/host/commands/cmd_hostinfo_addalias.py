#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2015 Dougal Scott
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

from host.models import getHost, HostAlias, getOrigin
from host.models import HostinfoCommand, HostinfoException


###############################################################################
class Command(HostinfoCommand):
    description = "Add alias to a host"

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument("host", help="The host to add the alias for")
        parser.add_argument("alias", help="The alias for the host")
        parser.add_argument("--origin", help="The origin of this alias")

    ###########################################################################
    def handle(self, namespace):
        origin = getOrigin(namespace.origin)
        host = namespace.host.lower()
        alias = namespace.alias.lower()
        targhost = getHost(host)
        if not targhost:
            raise HostinfoException("Host %s doesn't exist" % host)
        if getHost(alias):
            raise HostinfoException("Host %s already exists" % alias)
        haobj = HostAlias(hostid=targhost, alias=alias, origin=origin)
        haobj.save()
        return None, 0


# EOF
