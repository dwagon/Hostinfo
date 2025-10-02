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
from host.models import HostinfoCommand, HostinfoException
from host.models import getAliases, RestrictedValue
from host.models import getMatches, getAK, Host, getHost


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
        parser.add_argument("--origin", help="Print out origin of data", action="store_true")
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
        parser.add_argument("--valuereport", help="Print out frequencies of values", nargs=1)
        parser.add_argument("--host", help="For this specific host", nargs=1)
        parser.add_argument("--csv", help="Print data in CSV format", action="store_true")
        parser.add_argument("--xml", help="Print data in XML format", action="store_true")
        parser.add_argument("--json", help="Print data in JSON format", action="store_true")
        parser.add_argument("--sep", help="Use <str> as a value separator.", nargs=1, default=", ")
        parser.add_argument("--hsep", help="Use <str> as a host separator.", nargs=1, default="\n")
        parser.add_argument("--count", help="Return the number of matching hosts", action="store_true")
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
        return len(matches)

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
        kvlist = KeyValue.objects.filter(keyid__key=self.namespace.valuereport[0]).values_list(
            "hostid", "value", "numvalue"
        )

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

        outstr += f"{self.namespace.valuereport[0]} set: {nummatch} {100.0 * nummatch / total:0.2%}\n"
        outstr += f"{self.namespace.valuereport[0]} unset: {numundef} {100.0 * numundef / total:0.2%}\n"
        outstr += "\n"
        for k, v, p in tmpvalues:
            outstr += f"{k} {v} %0.2f%%\n" % p
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
                originstr = f"\t[Origin: {keyorig[key]}"
            else:
                originstr = ""

            if self.namespace.times:
                timestr = f"\t[Created: {keyctime[key]} Modified: {keymtime[key]}"
            else:
                timestr = ""
            output.append(f"    {key}: {self.namespace.sep[0].join(values):<15}%-15s{originstr}{timestr}")
        output.sort()

        # Generate the output for the hostname
        if self.namespace.origin:
            originstr = f"\t[Origin: {_hostcache[host].origin}]"
        else:
            originstr = ""
        if self.namespace.times:
            timestr = "\t[Created: {_hostcache[host].createdate} Modified: {_hostcache[host].modifieddate}]"
        else:
            timestr = ""

        # Output the pregenerated output
        output.insert(0, f"{_hostcache[host].hostname}{originstr}{timestr}")

        if self.namespace.aliases:
            alias_str = ", ".join(getAliases(_hostcache[host].hostname))
            output.insert(0, f"    [Aliases: {alias_str}]")

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
        outstr += f'  <query date="{time.ctime()}">{escape(" ".join(sys.argv))}</query>\n'
        for key in columns:
            k = getAK(key)
            outstr += "  <key>\n"
            outstr += f"    <name>{escape(key)}</name>\n"
            outstr += f"    <type>{k.get_validtype_display()}</type>\n"
            outstr += f"    <readonlyFlag>{k.readonlyFlag}</readonlyFlag>\n"
            outstr += f"    <auditFlag>{k.auditFlag}</auditFlag>\n"
            outstr += f"    <numericFlag>{k.numericFlag}</numericFlag>\n"
            outstr += f"    <docpage>{k.docpage}</docpage>\n"
            outstr += f"    <desc>{k.desc}</desc>\n"
            if k.restrictedFlag:
                outstr += "    <restricted>\n"
                rvlist = RestrictedValue.objects.filter(keyid__key=key)
                for rv in rvlist:
                    outstr += f"        <value>{escape(rv.value)}</value>\n"
                outstr += "    </restricted>\n"
            outstr += "  </key>\n"

        for host in matches:
            if self.namespace.aliases:
                aliaslist = getAliases(_hostcache[host].hostname)
            if self.namespace.origin:
                hostorigin = f' origin="{_hostcache[host].origin}" '
            else:
                hostorigin = ""
            if self.namespace.times:
                hostdates = f' modified="{_hostcache[host].modifieddate}" created="{_hostcache[host].createdate}" '
            else:
                hostdates = ""
            outstr += f'  <host docpage="{_hostcache[host].docpage}" {hostorigin}{hostdates}>\n'
            outstr += f"    <hostname>{escape(_hostcache[host].hostname)}</hostname>\n"
            if self.namespace.aliases and aliaslist:
                outstr += "    <aliaslist>\n"
                for alias in aliaslist:
                    outstr += f"      <alias>{escape(alias)}</alias>\n"
                outstr += "    </aliaslist>\n"
            outstr += "    <data>\n"
            for p in columns:
                if host not in cache[p] or len(cache[p][host]) == 0:
                    pass
                else:
                    for c in cache[p][host]:
                        outstr += f'      <confitem key="{p}"'
                        if self.namespace.origin:
                            outstr += f" origin={quoteattr(c['origin'])}"
                        if self.namespace.times:
                            outstr += f' modified="{c["modifieddate"]}" created="{c["createdate"]}"'
                        outstr += f">{escape(c['value'])}</confitem>\n"

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
            output.append(f"hostname{self.namespace.sep[0]}{self.namespace.sep[0].join(columns)}")

        for host in matches:
            outline = str(_hostcache[host].hostname)
            for p in columns:
                outline += self.namespace.sep[0]
                if host not in cache[p] or len(cache[p][host]) == 0:
                    pass
                else:
                    vals = sorted(cache[p][host], key=lambda x: x["value"])
                    val_str = self.namespace.sep[0].join([_["value"] for _ in vals])
                    outline += f'"{val_str}"'

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
            output = f"{_hostcache[host].hostname}\t"

            # Generate the output for the hostname
            if self.namespace.origin:
                output += f"[Origin: {_hostcache[host].origin}]\t"
            if self.namespace.times:
                output += f"[Created: {_hostcache[host].createdate} Modified: {_hostcache[host].modifieddate}]\t"

            for p in self.printout:
                val = ""
                if host not in cache[p]:
                    val = ""
                else:
                    for kv in sorted(cache[p][host], key=lambda x: x["value"]):
                        val += str(kv["value"])
                        if self.namespace.origin:
                            val += f"[Origin: {kv['origin']}]"
                        if self.namespace.times:
                            val += f"[Created: {kv['createdate']}, Modified: {kv['modifieddate']}"
                        val += self.namespace.sep[0]
                output += f"{p}={val[:-1]}\t"

            outstr += "{output.rstrip()}{self.namespace.hsep[0]}"
        if outstr and not outstr.endswith("\n"):
            outstr = f"{outstr[:-1]}\n"
        return outstr


# EOF
