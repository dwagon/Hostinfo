# Written by Dougal Scott <dougal.scott@gmail.com>

#    Copyright (C) 2012 Dougal Scott

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import xml.etree.ElementTree
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from host.models import HostinfoCommand
from host.models import HostinfoException
from host.models import RestrictedValueException, RestrictedValue
from host.models import Host, AllowedKey, KeyValue

_akcache = {}


###############################################################################
class Command(HostinfoCommand):
    description = "Import data from XML file"

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            "-k",
            dest="kiddingFlag",
            help="Don't actually do the import",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-v",
            dest="verboseFlag",
            help="Say what is happening",
            action="store_true",
            default=False,
        )
        parser.add_argument("xmlfile", help="The file to import from")

    ###########################################################################
    def handle(self, namespace):
        self.namespace = namespace
        try:
            xmltree = xml.etree.ElementTree.parse(namespace.xmlfile)
        except IOError as exc:
            if exc.errno == 2:
                raise HostinfoException("File %s doesn't exist" % namespace.xmlfile)
            else:
                raise HostinfoException(
                    "File %s not readable (errno=%d)" % (namespace.xmlfile, exc.errno)
                )

        for key in xmltree.findall("key"):
            self.handleKey(key)
        for host in xmltree.findall("host"):
            self.handleHost(host)
        return None, 0

    ###########################################################################
    def verbose(self, msg):
        if self.namespace.verboseFlag:
            sys.stderr.write("%s\n" % msg)

    ###########################################################################
    def validateKeytype(self, keytype):
        # Work out which type it should be
        vt = -1
        for knum, desc in AllowedKey.TYPE_CHOICES:
            try:
                if int(keytype) == knum:
                    vt = knum
                    break
            except ValueError:
                pass
            if keytype == desc:
                vt = knum
                break
        if vt < 0:
            raise HostinfoException(
                "Unknown type %s - should be one of %s"
                % (keytype, ",".join([d for k, d in AllowedKey.TYPE_CHOICES]))
            )
        return vt

    ###########################################################################
    def handleRestrictedKey(self, xmlbit, key):
        for kid in xmlbit.getchildren():
            value = kid.text
            try:
                rv = RestrictedValue.objects.get(keyid=key, value=value)
            except ObjectDoesNotExist:
                rv = RestrictedValue(keyid=key, value=value)
                self.verbose("Adding %s=%s to restricted key" % (key.key, value))
                if not self.namespace.kiddingFlag:
                    rv.save()

    ###########################################################################
    def handleKey(self, key):
        """
        <key>
          <name>appsla</name>
          <type>single</type>
          <readonlyFlag>True</readonlyFlag>
          <auditFlag>False</auditFlag>
          <restricted>
              <value>Foo</value>
          </restricted>
          <docpage>None</docpage>
          <desc>Application SLA</desc>
        </key>
        """

        name = ""
        keytype = ""
        restrictedKid = None
        restrictedFlag = False
        readonlyFlag = False
        auditFlag = True
        numericFlag = False
        docpage = ""
        desc = ""
        for kid in key.getchildren():
            if kid.tag == "name":
                name = kid.text
            if kid.tag == "type":
                keytype = self.validateKeytype(kid.text)
            if kid.tag == "restricted":
                restrictedKid = kid
                restrictedFlag = True
            if kid.tag == "readonlyFlag":
                readonlyFlag = kid.text == "True"
            if kid.tag == "auditFlag":
                auditFlag = kid.text == "True"
            if kid.tag == "numericFlag":
                numericFlag = kid.text == "True"
            if kid.tag == "docpage":
                if kid.text:
                    docpage = kid.text.strip()
                if docpage == "None":
                    docpage = None
            if kid.tag == "desc":
                if kid.text:
                    desc = kid.text.strip()
        if not name:
            raise HostinfoException("No name specified for key")

        try:
            ak = AllowedKey.objects.get(key=name)
        except ObjectDoesNotExist:
            ak = AllowedKey(
                key=name,
                validtype=keytype,
                restrictedFlag=restrictedFlag,
                readonlyFlag=readonlyFlag,
                auditFlag=auditFlag,
                numericFlag=numericFlag,
                docpage=docpage,
                desc=desc,
            )
            self.verbose("New key %s" % repr(ak))
            if not self.namespace.kiddingFlag:
                ak.save()
        else:
            change = False
            if ak.validtype != keytype:
                sys.stderr.write(
                    "Changing key types currently unsupported: %s\n" % name
                )
                sys.exit(1)
            if ak.restrictedFlag != restrictedFlag:
                self.verbose(
                    "Changing %s: restrictedFlag from %s to %s"
                    % (name, ak.restrictedFlag, restrictedFlag)
                )
                ak.restrictedFlag = restrictedFlag
                change = True
            if ak.readonlyFlag != readonlyFlag:
                self.verbose(
                    "Changing %s: readonlyFlag from %s to %s"
                    % (name, ak.readonlyFlag, readonlyFlag)
                )
                ak.readonlyFlag = readonlyFlag
                change = True
            if ak.auditFlag != auditFlag:
                self.verbose(
                    "Changing %s: auditFlag from %s to %s"
                    % (name, ak.auditFlag, auditFlag)
                )
                ak.auditFlag = auditFlag
                change = True
            if ak.docpage != docpage:
                self.verbose(
                    "Changing %s: docpage from '%s' to '%s'"
                    % (name, ak.docpage, docpage)
                )
                ak.docpage = docpage
                change = True
            if ak.desc != desc:
                self.verbose(
                    "Changing %s: desc from '%s' to '%s'" % (name, ak.desc, desc)
                )
                ak.desc = desc
                change = True
            if change and not self.namespace.kiddingFlag:
                ak.save()

        if restrictedKid is not None:
            self.handleRestrictedKey(restrictedKid, ak)

    ###########################################################################
    def handleHost(self, hosttree):
        """
        We can't load dates (created/modified) of elements because these are
        set automatically by Django

          <host docpage="None"  origin="explorer2hostinfo.py by w86765"  modified="2008-03-20" created="2008-03-20" >
            <hostname>zone_161.117.101.190</hostname>
            <data>
              <confitem key="os" origin="w86765" modified="2008-08-19" created="2008-08-19">solaris</confitem>
              <confitem key="type" origin="..." modified="2008-07-02" created="2008-03-20">virtual</confitem>
              <confitem key="virtualmaster" origin="..." modified="2008-03-20" created="2008-03-20">idmsvrqv01d</confitem>
              <confitem key="zonename" origin="..." modified="2008-03-20" created="2008-03-20">app04</confitem>
            </data>
          </host>
        """
        hostname = hosttree.find("hostname").text
        self.verbose(hostname)
        try:
            host = Host.objects.get(hostname=hostname)
        except ObjectDoesNotExist:
            host = Host(
                hostname=hostname,
                docpage=hosttree.attrib.get("docpage", None),
                origin=hosttree.attrib.get("origin", "unknown - import"),
            )
            self.verbose("New host %s" % repr(host))
            if not self.namespace.kiddingFlag:
                host.save()

        for data in hosttree.find("data").findall("confitem"):
            key = data.attrib["key"]
            if "origin" in data.attrib:
                origin = data.attrib["origin"]
            else:
                origin = "unknown"
            value = data.text
            try:
                self.handleValue(host, key, origin, value)
            except RestrictedValueException:
                sys.stderr.write(
                    "Trying to change a restricted value: %s:%s=%s - ignoring\n"
                    % (hostname, key, value)
                )

    ###########################################################################
    def getAllowedKey(self, key):
        if key in _akcache:
            return _akcache[key]
        _akcache[key] = AllowedKey.objects.get(key=key)
        return _akcache[key]

    ###########################################################################
    def handleValue(self, host, key, origin, value):
        # We allow changes to readonly keys as that is the whole point
        ak = self.getAllowedKey(key)
        if ak.get_validtype_display() == "list":
            try:
                kv = KeyValue.objects.get(hostid=host.id, keyid__key=key, value=value)
            except ObjectDoesNotExist:
                kv = KeyValue(hostid=host, keyid=ak, value=value, origin=origin)
                self.verbose("Appending %s: %s=%s" % (host.hostname, key, value))
                if not self.namespace.kiddingFlag:
                    kv.save(readonlychange=True)
            except MultipleObjectsReturned:
                pass
        else:
            try:
                kv = KeyValue.objects.get(hostid=host.id, keyid__key=key)
            except ObjectDoesNotExist:
                kv = KeyValue(hostid=host, keyid=ak, value=value, origin=origin)
                self.verbose("Creating %s: %s=%s" % (host.hostname, key, value))
                if not self.namespace.kiddingFlag:
                    kv.save(readonlychange=True)
            else:
                kv.value = value
                kv.origin = origin
                self.verbose("Replacing %s: %s=%s" % (host.hostname, key, value))
                if not self.namespace.kiddingFlag:
                    kv.save(readonlychange=True)


# EOF
