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
import sys
import time
from collections import defaultdict

from host.models import AllowedKey, KeyValue, parseQualifiers
from host.models import getMatches, getAK, Host, getHost
from host.models import getAliases, RestrictedValue
from host.models import HostinfoCommand, HostinfoException


###############################################################################
class Command(HostinfoCommand):
    description = "Retrieve details from hostinfo database"
    epilog = """
     Criteria:
        var=val\tMatch hosts that have a val equal to var (or var.eq.val)
        var!=val\tMatch hosts that have a val unequal to var (or var.ne.val)
        var~val\tMatch hosts that have a var containing the string val (or var.ss.val)
        var<val\tMatch hosts that have a val less than var (or var.lt.val)
        var>val\tMatch hosts that have a val greater than var (or var.gt.val)
        var.defined\tMatch hosts that have a val set
        var.undefined\tMatch hosts that don't have a val set
        str.hostre\tMatch hosts that have str in their name
        hostname\tMatch hosts that have the name hostname
    """

    ###########################################################################
    def parseArgs(self, parser):
        parser.add_argument(
            "--showall",
            help="Print everything known about the matching hosts",
            action="store_true",
        )
        parser.add_argument(
            "--origin", help="Print out origin of data", action="store_true"
        )
        parser.add_argument(
            "--aliases",
            help="Print out all aliases of matching host",
            action="store_true",
        )
        parser.add_argument(
            "--times",
            "--dates",
            help="Print out create and modification times of data",
            dest="times",
            action="store_true",
        )
        parser.add_argument(
            "--noheader",
            help="Don't print headers in CSV format",
            dest="header",
            action="store_false",
            default=True,
        )
        parser.add_argument(
            "--valuereport", help="Print out frequencies of values", nargs=1
        )
        parser.add_argument("--host", help="For this specific host", nargs=1)
        parser.add_argument(
            "--csv", help="Print data in CSV format", action="store_true"
        )
        parser.add_argument(
            "--xml", help="Print data in XML format", action="store_true"
        )
        parser.add_argument(
            "--json", help="Print data in JSON format", action="store_true"
        )
        parser.add_argument(
            "--sep", help="Use <str> as a value separator.", nargs=1, default=", "
        )
        parser.add_argument(
            "--hsep", help="Use <str> as a host separator.", nargs=1, default="\n"
        )
        parser.add_argument(
            "--count", help="Return the number of matching hosts", action="store_true"
        )
        parser.add_argument(
            "-p",
            help="Print values of key for matching hosts",
            action="append",
            dest="printout",
            default=[],
        )
        parser.add_argument("criteria", nargs="*")

    ###########################################################################
    def getHostCache(self, matches):
        c = {}
        for h in Host.objects.filter(id__in=matches):
            c[h.id] = h
        return c

    ###########################################################################
    def handle(self, namespace):
        global _hostcache
        self.namespace = namespace
        self.printout = namespace.printout
        if namespace.host:
            host = getHost(namespace.host[0])
            if host:
                matches = [host.id]
            else:
                matches = []
        else:
            try:
                qualifiers = parseQualifiers(namespace.criteria)
            except TypeError as err:  # pragma: no cover
                raise HostinfoException(err)
            matches = getMatches(qualifiers)
        _hostcache = self.getHostCache(matches)
        output = self.Display(matches)
        if matches:
            retval = 0
        else:
            retval = 1
        return output, retval

    ###########################################################################
    def Display(self, matches):
        """Display the list of hosts that matched the criteria"""
        # Sort the hosts alphabetically
        tmpl = [(_hostcache[id].hostname, id) for id in matches]
        tmpl.sort()
        matches = [id for name, id in tmpl]

        if self.namespace.valuereport:
            return self.DisplayValuereport(matches)
        elif self.namespace.csv:
            return self.DisplayCSV(matches)
        elif self.namespace.xml:
            return self.DisplayXML(matches)
        elif self.namespace.json:
            return self.DisplayJson(matches)
        elif self.namespace.showall:
            return self.DisplayShowall(matches)
        elif self.namespace.count:
            return self.DisplayCount(matches)
        else:
            return self.DisplayNormal(matches)

    ###########################################################################
    def DisplayCount(self, matches):
        """Display a count of matching hosts"""
        return "%s" % len(matches)

    ###########################################################################
    def DisplayValuereport(self, matches):
        """Display a report about the values a key has and how many hosts have
        that particular value
        """
        # TODO: Migrate to using calcKeylistVals
        outstr = ""
        values = defaultdict(int)
        hostids = set()  # hostids that match the criteria
        key = getAK(self.namespace.valuereport[0])
        total = len(matches)
        if total == 0:
            return ""
        nummatch = 0
        kvlist = KeyValue.objects.filter(
            keyid__key=self.namespace.valuereport[0]
        ).values_list("hostid", "value", "numvalue")

        for hostid, value, numvalue in kvlist:
            hostids.add(hostid)
            if key.numericFlag and numvalue is not None:
                values[numvalue] += 1
            else:
                values[value] += 1
        nummatch = len(hostids)  # Number of hosts that match
        numundef = total - len(hostids)

        tmpvalues = []
        for k, v in values.items():
            p = 100.0 * v / nummatch
            tmpvalues.append((k, v, p))

        tmpvalues.sort()

        outstr += "%s set: %d %0.2f%%\n" % (
            self.namespace.valuereport[0],
            nummatch,
            100.0 * nummatch / total,
        )
        outstr += "%s unset: %d %0.2f%%\n" % (
            self.namespace.valuereport[0],
            numundef,
            100.0 * numundef / total,
        )
        outstr += "\n"
        for k, v, p in tmpvalues:
            outstr += "%s %d %0.2f%%\n" % (k, v, p)
        return outstr

    ###########################################################################
    def DisplayShowall(self, matches):
        """Display all the known information about the matched hosts"""
        revcache = {}
        outputs = []
        for aks in AllowedKey.objects.all():
            revcache[aks.id] = aks.key

        batchsize = 10
        batches = []
        for b in range(0, len(matches), batchsize):
            batches.append(matches[b : b + batchsize])

        for batch in batches:
            kvs = KeyValue.objects.filter(hostid__in=batch)
            for host in batch:
                outputs.append(self.gen_host(host, kvs, revcache))
        return "\n".join(outputs)

    ###########################################################################
    def gen_host(self, host, kvs, revcache):
        outstr = ""
        output = []
        keyvals = {}
        keyorig = {}
        keyctime = {}
        keymtime = {}

        # Get all the keyvalues for this host
        for k in kvs:
            if k.hostid_id != host:
                continue
            keyname = revcache[k.keyid_id]
            if keyname not in keyvals:
                keyvals[keyname] = []
            keyvals[keyname].append(k.value)
            keyorig[keyname] = k.origin
            keyctime[keyname] = k.createdate
            keymtime[keyname] = k.modifieddate

        # Generate the output string for each key/value pair
        for key, values in keyvals.items():
            values.sort()
            if self.namespace.origin:
                originstr = "\t[Origin: %s]" % keyorig[key]
            else:
                originstr = ""

            if self.namespace.times:
                timestr = "\t[Created: %s Modified: %s]" % (
                    keyctime[key],
                    keymtime[key],
                )
            else:
                timestr = ""
            output.append(
                "    %s: %-15s%s%s"
                % (key, self.namespace.sep[0].join(values), originstr, timestr)
            )
        output.sort()

        # Generate the output for the hostname
        if self.namespace.origin:
            originstr = "\t[Origin: %s]" % _hostcache[host].origin
        else:
            originstr = ""
        if self.namespace.times:
            timestr = "\t[Created: %s Modified: %s]" % (
                _hostcache[host].createdate,
                _hostcache[host].modifieddate,
            )
        else:
            timestr = ""

        # Output the pregenerated output
        output.insert(0, "%s%s%s" % (_hostcache[host].hostname, originstr, timestr))

        if self.namespace.aliases:
            output.insert(
                0,
                "    [Aliases: %s]"
                % (", ".join(getAliases(_hostcache[host].hostname))),
            )

        outstr += "\n".join(output)
        return outstr

    ###########################################################################
    def DisplayXML(self, matches):
        """Display hosts and other printables in XML format"""
        from xml.sax.saxutils import escape, quoteattr

        outstr = ""

        if self.namespace.showall:
            columns = [k.key for k in AllowedKey.objects.all()]
            columns.sort()
        else:
            columns = self.printout[:]

        cache = self.loadPrintoutCache(columns, matches)
        outstr += "<hostinfo>\n"
        outstr += '  <query date="%s">%s</query>\n' % (
            time.ctime(),
            escape(" ".join(sys.argv)),
        )
        for key in columns:
            k = getAK(key)
            outstr += "  <key>\n"
            outstr += "    <name>%s</name>\n" % escape(key)
            outstr += "    <type>%s</type>\n" % k.get_validtype_display()
            outstr += "    <readonlyFlag>%s</readonlyFlag>\n" % k.readonlyFlag
            outstr += "    <auditFlag>%s</auditFlag>\n" % k.auditFlag
            outstr += "    <numericFlag>%s</numericFlag>\n" % k.numericFlag
            outstr += "    <docpage>%s</docpage>\n" % k.docpage
            outstr += "    <desc>%s</desc>\n" % k.desc
            if k.restrictedFlag:
                outstr += "    <restricted>\n"
                rvlist = RestrictedValue.objects.filter(keyid__key=key)
                for rv in rvlist:
                    outstr += "        <value>%s</value>\n" % escape(rv.value)
                outstr += "    </restricted>\n"
            outstr += "  </key>\n"

        for host in matches:
            if self.namespace.aliases:
                aliaslist = getAliases(_hostcache[host].hostname)
            if self.namespace.origin:
                hostorigin = ' origin="%s" ' % _hostcache[host].origin
            else:
                hostorigin = ""
            if self.namespace.times:
                hostdates = ' modified="%s" created="%s" ' % (
                    _hostcache[host].modifieddate,
                    _hostcache[host].createdate,
                )
            else:
                hostdates = ""
            outstr += '  <host docpage="%s" %s%s>\n' % (
                _hostcache[host].docpage,
                hostorigin,
                hostdates,
            )
            outstr += "    <hostname>%s</hostname>\n" % escape(
                _hostcache[host].hostname
            )
            if self.namespace.aliases and aliaslist:
                outstr += "    <aliaslist>\n"
                for alias in aliaslist:
                    outstr += "      <alias>%s</alias>\n" % escape(alias)
                outstr += "    </aliaslist>\n"
            outstr += "    <data>\n"
            for p in columns:
                if host not in cache[p] or len(cache[p][host]) == 0:
                    pass
                else:
                    for c in cache[p][host]:
                        outstr += '      <confitem key="%s"' % p
                        if self.namespace.origin:
                            outstr += " origin=%s" % quoteattr(c["origin"])
                        if self.namespace.times:
                            outstr += ' modified="%s" created="%s"' % (
                                c["modifieddate"],
                                c["createdate"],
                            )
                        outstr += ">%s</confitem>\n" % escape(c["value"])

            outstr += "    </data>\n"
            outstr += "  </host>\n"
        outstr += "</hostinfo>\n"
        return outstr

    ###########################################################################
    def DisplayJson(self, matches):
        """Display hosts and other printables in JSON format"""
        import json

        if self.namespace.showall:
            columns = [k.key for k in AllowedKey.objects.all()]
            columns.sort()
        else:
            columns = self.printout[:]

        cache = self.loadPrintoutCache(columns, matches)

        data = {}
        for host in matches:
            hname = _hostcache[host].hostname
            data[hname] = {}
            for p in columns:
                if host not in cache[p] or len(cache[p][host]) == 0:
                    pass
                else:
                    data[hname][p] = []
                    for c in cache[p][host]:
                        data[hname][p].append(c["value"])

        return json.dumps(data)

    ###########################################################################
    def DisplayCSV(self, matches):
        """Display hosts and other printables in CSV format"""
        output = []
        if self.namespace.showall:
            columns = [k.key for k in AllowedKey.objects.all()]
            columns.sort()
        else:
            columns = self.printout[:]

        cache = self.loadPrintoutCache(columns, matches)

        if self.namespace.header:
            output.append(
                "hostname%s%s"
                % (self.namespace.sep[0], self.namespace.sep[0].join(columns))
            )

        for host in matches:
            outline = "%s" % _hostcache[host].hostname
            for p in columns:
                outline += self.namespace.sep[0]
                if host not in cache[p] or len(cache[p][host]) == 0:
                    pass
                else:
                    vals = sorted(cache[p][host], key=lambda x: x["value"])
                    outline += '"%s"' % (
                        self.namespace.sep[0].join([c["value"] for c in vals])
                    )

            output.append(outline)
        return "\n".join(output)

    ###########################################################################
    def loadPrintoutCache(self, columns, matches=None):
        # Load all the information that we have been requested into a cache
        cache = {}
        for p in columns:
            getAK(p)
            cache[p] = {}
            allv = KeyValue.objects.filter(keyid=getAK(p).id).values()
            for val in allv:
                hostid = val["hostid_id"]
                if matches and hostid not in matches:
                    continue
                try:
                    cache[p][hostid].append(val)
                except KeyError:
                    cache[p][hostid] = [val]
        return cache

    ###########################################################################
    def DisplayNormal(self, matches):
        """Display hosts and other printables to stdout in human readable format"""
        cache = self.loadPrintoutCache(self.printout, matches)
        outstr = ""

        for host in matches:
            output = "%s\t" % _hostcache[host].hostname

            # Generate the output for the hostname
            if self.namespace.origin:
                output += "[Origin: %s]\t" % _hostcache[host].origin
            if self.namespace.times:
                output += "[Created: %s Modified: %s]\t" % (
                    _hostcache[host].createdate,
                    _hostcache[host].modifieddate,
                )

            for p in self.printout:
                val = ""
                if host not in cache[p]:
                    val = ""
                else:
                    for kv in sorted(cache[p][host], key=lambda x: x["value"]):
                        val += "%s" % kv["value"]
                        if self.namespace.origin:
                            val += "[Origin: %s]" % kv["origin"]
                        if self.namespace.times:
                            val += "[Created: %s, Modified: %s]" % (
                                kv["createdate"],
                                kv["modifieddate"],
                            )
                        val += self.namespace.sep[0]
                output += "%s=%s\t" % (p, val[:-1])

            outstr += "%s%s" % (output.rstrip(), self.namespace.hsep[0])
        if outstr and not outstr.endswith("\n"):
            outstr = "%s%s" % (outstr[:-1], "\n")
        return outstr


# EOF
