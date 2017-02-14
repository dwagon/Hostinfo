#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2017 Dougal Scott
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

from host.models import getHost
from host.models import HostinfoCommand, HostinfoException, Links


###############################################################################
class Command(HostinfoCommand):
    description = 'Delete a link to a host'

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument('--everytag', help='Delete all links', action='store_true')
        parser.add_argument('--tag', help='The link tag', nargs=1)
        parser.add_argument('host', help='The host to delete the link from')

    ###########################################################################
    def handle(self, namespace):
        host = namespace.host.lower()
        targhost = getHost(host)
        if not targhost:
            raise HostinfoException("Host %s doesn't exist" % host)
        links = Links.objects.filter(hostid=targhost)
        if namespace.everytag:
            pass
        if namespace.tag:
            links = links.filter(tag=namespace.tag[0].lower())
        for link in links:
            link.delete()
        return None, 0

# EOF
