"""hostinfo_addvalue command"""

#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2025 Dougal Scott
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

import os
import re
import sys

from host.models import HostinfoCommand
from host.models import ReadonlyValueException, HostinfoException
from host.models import RestrictedValueException
from host.models import addKeytoHost


###############################################################################
class Command(HostinfoCommand):
    """hostinfo_addvalue"""

    description = "Add a value to a hosts key"

    ###########################################################################
    def parseArgs(self, parser):
        """Parse args"""

        parser.add_argument("-o", "--origin", help="The origin of this data")
        parser.add_argument("-a", "--append", help="Append to a list type key", action="store_true")
        parser.add_argument("-u", "--update", help="Replace an existing value", action="store_true")
        parser.add_argument("--readonlyupdate", help="Write to a readonly key", action="store_true")
        parser.add_argument("keyvalue", help="Name of the key/value pair to add (key=value)")
        parser.add_argument("host", help="Host(s) to add this value to", nargs="+")

    ###########################################################################
    def handle(self, namespace):
        """do command"""

        m = re.match(r"(?P<key>\w+)=(?P<value>.+)", namespace.keyvalue)
        if not m:
            raise HostinfoException("Must be specified in key=value format")
        key = m.group("key").lower()
        value = m.group("value").lower()
        if not namespace.origin:
            namespace.origin = os.path.basename(sys.argv[0])
        for host in namespace.host:
            host = host.lower().strip()
            try:
                addKeytoHost(
                    host=host,
                    key=key,
                    value=value,
                    origin=namespace.origin,
                    readonlyFlag=namespace.readonlyupdate,
                    updateFlag=namespace.update,
                    appendFlag=namespace.append,
                )
            except RestrictedValueException as exc:
                raise RestrictedValueException(
                    f"Cannot add {key}={value} to a restricted key",
                    key=key,
                    retval=2,
                ) from exc
            except ReadonlyValueException as exc:
                raise ReadonlyValueException(f"Cannot add {key}={value} to a readonly key", retval=3) from exc
            except HostinfoException as exc:
                raise
            except TypeError as exc:  # pragma: nocover
                raise HostinfoException(f"Couldn't add value {value} to {host} - {exc}") from exc
        return None, 0


# EOF
