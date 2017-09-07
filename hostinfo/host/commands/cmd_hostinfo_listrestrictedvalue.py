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
# Script to list the legal values of a restricted key

from host.models import AllowedKey, RestrictedValue, HostinfoException
from host.models import HostinfoCommand


###############################################################################
class Command(HostinfoCommand):
    description = 'List all allowable values of a restricted key'

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument('key', help='Name of the key to list')

    ###########################################################################
    def handle(self, namespace):
        outstr = ""
        key = namespace.key.lower()
        keyobjlist = AllowedKey.objects.filter(key=key)
        if len(keyobjlist) != 1:
            raise HostinfoException("No key %s found" % key)

        vals = []
        rvallist = RestrictedValue.objects.filter(keyid=keyobjlist[0])
        for rv in rvallist:
            vals.append(rv.value)
        for rv in sorted(vals):
            outstr += "%s\n" % rv
        return outstr, 0

# EOF
