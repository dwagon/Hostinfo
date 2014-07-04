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

import sys
from host.models import getHost, HostinfoException, KeyValue
from host.models import HostinfoCommand
from django.core.exceptions import ObjectDoesNotExist


###############################################################################
class Command(HostinfoCommand):
    description = 'Merge two hosts'

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            '-f', '--force',
            help="Force the merge", action='store_true')
        parser.add_argument(
            '-k', '--kidding',
            help="Don't actually make any changes", action='store_true')
        parser.add_argument(
            '--src',
            help='The source host', nargs=1, required=True, dest='srchost')
        parser.add_argument(
            '--dst',
            help='The destination host', nargs=1, required=True, dest='dsthost')

    ###########################################################################
    def handle(self, namespace):
        self.kidding = namespace.kidding
        srchostobj = getHost(namespace.srchost[0])
        if not srchostobj:
            raise HostinfoException("Source host %s doesn't exist" % namespace.srchost[0])
        dsthostobj = getHost(namespace.dsthost[0])
        if not dsthostobj:
            raise HostinfoException("Destination host %s doesn't exist" % namespace.dsthost[0])

        ok = True

        # Get all the key/values from the source host and see if they exist on the dest host
        srckeylist = KeyValue.objects.filter(hostid__hostname=namespace.srchost[0])
        for srckey in srckeylist:
            ok = self.transferKey(srckey, srchostobj, dsthostobj)
            if not ok:
                break

        if ok and not namespace.kidding:
            srchostobj.delete()
        return None, 0

    ###############################################################################
    def transferKey(self, srckey, srchostobj, dsthostobj):
        """ Transfer the key from the source host to the dest host
        """
        keytype = srckey.keyid.get_validtype_display()
        if keytype == "list":
            return self.transferListKey(srckey, srchostobj, dsthostobj)
        else:
            return self.transferSingleKey(srckey, srchostobj, dsthostobj)

    ###############################################################################
    def transferListKey(self, srckey, srchostobj, dsthostobj):
        """ Transfer a list key from srchost to dsthost
        """
        dstkeys = KeyValue.objects.filter(hostid=dsthostobj, keyid=srckey.keyid)
        dstvals = [k.value for k in dstkeys]
        if srckey.value in dstvals:
            if not self.kidding:
                srckey.delete(readonlychange=True)
        else:
            if not self.kidding:
                srckey.hostid = dsthostobj
                srckey.save(readonlychange=True)
        return True

    ###############################################################################
    def transferSingleKey(self, srckey, srchostobj, dsthostobj):
        """ Transfer a single or date key from srchost to dsthost
        """
        try:
            dstkey = KeyValue.objects.get(hostid=dsthostobj, keyid=srckey.keyid)
        except ObjectDoesNotExist:
            # If the dest key doesn't exist then copy the src key to it
            if not self.kidding:
                srckey.hostid = dsthostobj
                srckey.save(readonlychange=True)
            return True

        if dstkey.value != srckey.value:
            if self.force:
                if not self.kidding:
                    srckey.delete(readonlychange=True)
            else:
                sys.stderr.write("Collision: %s src=%s dst=%s\n" % (srckey.keyid, srckey.value, dstkey.value))
                sys.stderr.write("To keep dst %s value %s: hostinfo_addvalue --update %s='%s' %s\n" % (dsthostobj, dstkey.value, dstkey.keyid, dstkey.value, srchostobj))
                sys.stderr.write("To keep src %s value %s: hostinfo_addvalue --update %s='%s' %s\n" % (srchostobj, srckey.value, srckey.keyid, srckey.value, dsthostobj))
                return False
        else:
            if not self.kidding:
                # Data is the same so delete the src
                srckey.delete(readonlychange=True)
        return True

#EOF
