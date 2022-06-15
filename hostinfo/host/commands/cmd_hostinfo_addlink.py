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

from host.models import getHost
from host.models import HostinfoCommand, HostinfoException, Links


###############################################################################
class Command(HostinfoCommand):
    description = "Associate a link with a host"

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument("tag", help="The link tag")
        parser.add_argument("url", help="The url for the link")
        parser.add_argument("host", help="The host to add the link to")
        parser.add_argument(
            "-f",
            "--force",
            help="Force add the link with no checking",
            action="store_true",
        )
        parser.add_argument(
            "--update",
            help="Overwrite existing url for the same tag",
            action="store_true",
        )

    ###########################################################################
    def handle(self, namespace):
        host = namespace.host.lower()
        tag = namespace.tag.lower()
        url = namespace.url.lower()
        targhost = getHost(host)
        # Add url validation
        if not targhost:
            raise HostinfoException("Host %s doesn't exist" % host)
        link = Links.objects.filter(hostid=targhost, tag=tag)
        if link:
            if namespace.update:
                link[0].url = url
                link[0].save()
                return None, 0
            else:
                return "Host %s already has a link with tag %s" % (host, tag), 1
        link = Links(hostid=targhost, tag=tag, url=url)
        link.save()
        return None, 0


# EOF
