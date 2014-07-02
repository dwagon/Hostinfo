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
from hostinfo.host.models import UndoLog
from hostinfo.host.models import HostinfoCommand
import os
import datetime


###############################################################################
class Command(HostinfoCommand):
    description = 'Display the undolog'

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            '--user', help='Print the undolog for the specified user', nargs=1)
        parser.add_argument(
            '--week', help='Print the undolog the the last week',
            dest='days', const=[7], action='store_const')
        parser.add_argument(
            '--days', help='Print the undo log for the specified number of days',
            nargs=1, type=int)

    ###########################################################################
    def handle(self, namespace):
        outstr = ""
        now = datetime.datetime.now()
        if not namespace.days:
            namespace.days = [1]
        then = now-datetime.timedelta(days=namespace.days[0])
        if namespace.user:
            user = namespace.user[0]
        else:
            user = os.getlogin()
        ulog = UndoLog.objects.filter(user=user, actiondate__gte=then)
        for undoact in ulog:
            outstr += "%-55s # %s\n" % (undoact.action, undoact.actiondate)
        return outstr, 0

#EOF
