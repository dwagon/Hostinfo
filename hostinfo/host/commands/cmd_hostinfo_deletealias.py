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
from hostinfo.host.models import HostAlias, HostinfoException
from hostinfo.host.models import HostinfoCommand

class Command(HostinfoCommand):
    description='Delete an alias from a host'

    ############################################################################
    def parseArgs(self, parser):
        parser.add_argument('alias',help='The alias to delete')

    ############################################################################
    def handle(self, namespace):
        alias=namespace.alias.lower()
        aliases=HostAlias.objects.filter(alias=alias)
        if len(aliases)==0:
            raise HostinfoException("No alias called %s" % alias)
        aliases[0].delete()
        return None,0

#EOF
