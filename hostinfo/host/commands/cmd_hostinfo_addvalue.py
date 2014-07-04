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

import re
from hostinfo.host.models import addKeytoHost
from hostinfo.host.models import RestrictedValueException
from hostinfo.host.models import ReadonlyValueException, HostinfoException
from hostinfo.host.models import HostinfoCommand


###############################################################################
class Command(HostinfoCommand):
    description = 'Add a value to a hosts key'

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument('-o', '--origin', help='The origin of this data')
        parser.add_argument('-a', '--append', help='Append to a list type key', action='store_true')
        parser.add_argument('-u', '--update', help='Replace an existing value', action='store_true')
        parser.add_argument('--readonlyupdate', help='Write to a readonly key', action='store_true')
        parser.add_argument('keyvalue', help='Name of the key/value pair to add (key=value)')
        parser.add_argument('host', help='Host(s) to add this value to', nargs='+')

    ###########################################################################
    def handle(self, namespace):
        m = re.match("(?P<key>\w+)=(?P<value>.+)", namespace.keyvalue)
        if not m:
            raise HostinfoException("Must be specified in key=value format")
        key = m.group('key').lower()
        value = m.group('value').lower()
        for host in namespace.host:
            host = host.lower().strip()
            try:
                addKeytoHost(
                    host, key, value, origin=namespace.origin,
                    readonlyFlag=namespace.readonlyupdate,
                    updateFlag=namespace.update, appendFlag=namespace.append)
            except RestrictedValueException:
                raise RestrictedValueException(
                    "Cannot add %s=%s to a restricted key" % (key, value),
                    key=key, retval=2)
            except ReadonlyValueException:
                raise ReadonlyValueException(
                    "Cannot add %s=%s to a readonly key" % (key, value),
                    retval=3)
            except HostinfoException, err:
                raise
            except TypeError, err:  # pragma: nocover
                raise HostinfoException("Couldn't add value %s to %s - %s" % (value, host, err))
        return None, 0

#EOF
