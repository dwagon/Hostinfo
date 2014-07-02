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
from hostinfo.host.models import getHost, HostinfoException
from hostinfo.host.models import HostinfoCommand


###############################################################################
class Command(HostinfoCommand):
    description = 'Rename a host'

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            '--src',
            help="The current name of the host", nargs=1, dest='srchost')
        parser.add_argument(
            '--dst',
            help="The new name of the host", nargs=1, dest='dsthost')

    ###########################################################################
    def handle(self, namespace):
        hostobj = getHost(namespace.srchost[0])
        if not hostobj:
            raise HostinfoException("There is no host called %s" % namespace.srchost[0])
        dsthostobj = getHost(namespace.dsthost[0])
        if dsthostobj:
            raise HostinfoException("A host already exists with the name %s" % namespace.dsthost[0])
        hostobj.hostname = namespace.dsthost[0]
        hostobj.save()
        return None, 0

#EOF
