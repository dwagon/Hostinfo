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

#from hostinfo.host.models import AllowedKey, HostinfoException
#from hostinfo.host.models import HostinfoCommand

import hostinfo.host.models


###############################################################################
class Command(hostinfo.host.models.HostinfoCommand):
    description = 'Report on available keys'

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            '--type',
            help='Display just the types', dest='typeflag', action='store_true')
        parser.add_argument(
            'keylist',
            help="List of keys to display. Defaults to all", nargs='*')

    ###########################################################################
    def handle(self, namespace):
        outstr = ""
        allkeys = hostinfo.host.models.AllowedKey.objects.all()
        if namespace.keylist:
            keys = [k for k in allkeys if k.key in namespace.keylist]
        else:
            keys = [k for k in allkeys]

        if not keys:
            raise hostinfo.host.models.HostinfoException("No keys to show")

        for key in keys:
            if namespace.typeflag:
                outstr += "%s\t%s\n" % (key.key, key.get_validtype_display())
            else:
                notes = ""
                if key.restrictedFlag:
                    notes = "\t[KEY RESTRICTED]"
                if key.readonlyFlag:
                    notes += "\t[KEY READ ONLY]"
                outstr += "%s\t%s\t%s%s\n" % (key.key, key.get_validtype_display(), key.desc, notes)
        return outstr, 0

#EOF
