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

import re
from host.models import RestrictedValue, HostinfoException
from host.models import HostinfoCommand


###############################################################################
class Command(HostinfoCommand):
    description = "Remove an allowable value from a restricted key"

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            "keyvalue", help="Name of the key/value pair to disallow (key=value)"
        )

    ###########################################################################
    def handle(self, namespace):
        m = re.match("(?P<key>\w+)=(?P<value>.+)", namespace.keyvalue)
        if not m:
            raise HostinfoException("Must be specified in key=value format")
        key = m.group("key").lower()
        value = m.group("value").lower()
        rvallist = RestrictedValue.objects.filter(keyid__key=key, value=value)
        if len(rvallist) != 1:
            raise HostinfoException(
                "No key %s=%s in the restrictedvalue list" % (key, value)
            )
        rvallist[0].delete()
        return None, 0


# EOF
