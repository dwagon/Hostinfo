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

from host.models import getHost, HostAlias, HostinfoException
from host.models import HostinfoCommand


###############################################################################
class Command(HostinfoCommand):
    description = "List aliases"

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            "-a", "--all", help="List aliases for all hosts", action="store_true"
        )
        parser.add_argument(
            "host", help="List the aliases for this host only", nargs="?"
        )

    ###########################################################################
    def handle(self, namespace):
        outstr = ""
        if namespace.all or not namespace.host:
            aliases = HostAlias.objects.all().order_by("alias").select_related("hostid")
            for alias in aliases:
                outstr += "%s %s\n" % (alias.alias, alias.hostid.hostname)
            return outstr, 0
        hid = getHost(namespace.host.lower())
        if not hid:
            raise HostinfoException("Host %s doesn't exist" % namespace.host)
        outstr += "%s\n" % hid.hostname
        aliases = HostAlias.objects.filter(hostid=hid).order_by("alias")
        if not aliases:
            return outstr, 1
        for alias in aliases:
            outstr += "%s\n" % alias.alias

        return outstr, 0


# EOF
