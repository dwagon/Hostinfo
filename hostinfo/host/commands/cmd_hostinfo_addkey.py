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
from host.models import AllowedKey, HostinfoException
from host.models import HostinfoCommand

class Command(HostinfoCommand):
    description='Add a new key'
    type_choices=[d for k,d in AllowedKey.TYPE_CHOICES]

    ############################################################################
    def parseArgs(self, parser):
        parser.add_argument('--restricted',help="The key is resricted - can only take specific values", action='store_true', default=False)
        parser.add_argument('--readonly',help="The key is readonly - can only be changed with extra effort", action='store_true', default=False)
        parser.add_argument('--noaudit',help="Changes to this key won't be audited", action='store_false', default=True, dest='audit')
        parser.add_argument('--keytype',help="Type of key", choices=self.type_choices, default=None)
        parser.add_argument('key',help="Name of the key to add [keytype [description of key]]", nargs='+')

    ############################################################################
    def handle(self, namespace):
        desc=""
        if namespace.keytype:
            keytype=namespace.keytype
            desc=" ".join(namespace.key[1:])
        else:
            if len(namespace.key)==1:
                keytype='single'
            else:
                keytype=namespace.key[1]
            desc=" ".join(namespace.key[2:])
        key=namespace.key[0].lower()
        keytype=self.validateKeytype(keytype)
        try:
            AllowedKey.objects.get(key=key)
        except:
            newak=AllowedKey(key=key, validtype=keytype, desc=desc, restrictedFlag=namespace.restricted, readonlyFlag=namespace.readonly, auditFlag=namespace.audit)
            newak.save()
        else:
            raise HostinfoException("Key already exists with that name: %s" % key)
        return None,0

    ############################################################################
    def validateKeytype(self,keytype):
        # Work out which type it should be
        vt=-1
        for knum,desc in AllowedKey.TYPE_CHOICES:
            if keytype==desc:
                vt=knum
                break
        if vt<0:
            raise HostinfoException("Unknown type %s - should be one of %s" % (keytype, ",".join(self.type_choices)))
        return vt
#EOF
