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

# Script to show the history of an host
# Unfortunately due to the way foreignkeys work all audits details about a host's
# keys are deleted with the host
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from host.models import Host, KeyValue, AllowedKey
from host.models import HostinfoCommand, HostinfoInternalException

class Command(HostinfoCommand):
    description='Add alias to a host'
    _keycache={}

    ############################################################################
    def parseArgs(self, parser):
        parser.add_argument('-o','--origin',help='Show the origin of the change', action='store_true', dest='originFlag')
        parser.add_argument('-a','--actor',help='Show the actor of the change', action='store_true', dest='actorFlag')
        parser.add_argument('host',help='Host to show the history of')

    ############################################################################
    def handle(self, namespace):
        outstr=""
        hostidlist=self.getHostids(namespace.host)
        changelist=[]
        for hostid in hostidlist:
            changelist.extend(self.getHostChanges(hostid, namespace.host, namespace.originFlag, namespace.actorFlag))
            changelist.extend(self.getKeyChanges(hostid, namespace.host, namespace.originFlag, namespace.actorFlag))

        changelist.sort()
        for date,change in changelist:
            outstr+=change
        return outstr,0

    ############################################################################
    def getKeyName(self, keyid):
        if keyid in self._keycache:
            return self._keycache[keyid]
        try:
            key=AllowedKey.objects.get(id=keyid).key
        except ObjectDoesNotExist:
            key="<deleted>"
        self._keycache[keyid]=key
        return key

    ############################################################################
    def changetype(self, chtype):
        if chtype=='U':
            return "changed"
        elif chtype=='I':
            return "added"
        elif chtype=='D':
            return "deleted"
            
    ############################################################################
    def getHostids(self, hostname):
        # We have to get evil and use raw SQL as we need to be able to look up
        # the details of objects that no longer exist except in the audit log
        # We also get a host.id the normal way in case the host was created before
        # the audit log was created (or trimmed)
        cursor=connection.cursor()
        cursor.execute("SELECT DISTINCT id FROM host_host_audit WHERE hostname=%s", [hostname])
        ans=cursor.fetchall()
        hostids=[x[0] for x in ans]
        cursor.close()

        try:
            host=Host.objects.get(hostname=hostname)
            if host.id not in hostids:
                hostids.append(host.id)
        except ObjectDoesNotExist:
            pass
        return hostids

    ############################################################################
    def getHostChanges(self, hostid, hostname, originFlag, actorFlag):
        # More evil
        cursor=connection.cursor()
        cursor.execute("SELECT hostname, user, _audit_timestamp, _audit_change_type, actor, origin FROM host_host_audit WHERE id=%d" % hostid)
        rows=cursor.fetchall()
        cursor.close()
        ans=[]
        for row in rows:
            msg="%s %s %s on %s" % (row[1], self.changetype(row[3]), hostname, row[2])
            if actorFlag:
                msg+=" using %s" % row[4]
            if originFlag:
                msg+=" origin %s" % row[5]
            ans.append((row[2],"%s\n" % msg))
        return ans

    ############################################################################
    def getKeyChanges(self, hostid, hostname, originFlag, actorFlag):
        # More unavoidable evil
        cursor=connection.cursor()
        cursor.execute("SELECT keyid_id, value, user, _audit_timestamp, _audit_change_type, actor, origin FROM host_keyvalue_audit WHERE hostid_id=%d" % hostid)
        rows=cursor.fetchall()
        cursor.close()

        ans=[]
        for row in rows:
            key=self.getKeyName(row[0])
            msg="%s %s %s:%s on %s on %s" % (row[2], self.changetype(row[4]), key, row[1], hostname, row[3])
            if actorFlag:
                msg+=" using %s" % row[5]
            if originFlag:
                msg+=" origin %s" % row[6]
            ans.append((row[3],"%s\n" % msg))
        return ans
            
#EOF
