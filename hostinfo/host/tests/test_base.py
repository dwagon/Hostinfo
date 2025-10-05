"""Test rig for hostinfo"""

# Written by Dougal Scott <dougal.scott@gmail.com>

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

import json
import sys
import time

from django.test import TestCase
from django.test.client import Client
from host.edits import getHostMergeKeyData
from host.models import Host, HostAlias, AllowedKey, Links
from host.models import HostinfoException
from host.models import addKeytoHost, KeyValue
from host.models import getHost, checkHost, getAK
from host.models import parseQualifiers, getMatches, Qualifier
from host.models import validateDate, clearAKcache, calcKeylistVals
from host.views import hostviewrepr, hostData
from host.views import orderHostList


###############################################################################
class test_DateValidator(TestCase):
    """Test validateDate()"""

    ###########################################################################
    def test_formats(self):
        """Test different date formats"""
        self.assertEqual(validateDate("2012-12-31"), "2012-12-31")
        self.assertEqual(validateDate("31/12/2012"), "2012-12-31")
        self.assertEqual(validateDate("31/12/12"), "2012-12-31")
        self.assertEqual(validateDate("2012/12/31"), "2012-12-31")

    ###########################################################################
    def test_today(self):
        """Does today equal now"""
        now = time.strftime("%Y-%m-%d")
        self.assertEqual(validateDate("now"), now)
        self.assertEqual(validateDate("today"), now)


###############################################################################
class test_HostAlias(TestCase):
    """Test HostAlias class"""

    def setUp(self):
        clearAKcache()
        self.host = Host(hostname="host")
        self.host.save()
        self.alias = HostAlias(hostid=self.host, alias="alias")
        self.alias.save()

    ###########################################################################
    def tearDown(self):
        self.alias.delete()
        self.host.delete()

    def test_alias(self):
        a = HostAlias.objects.all()[0]
        self.assertEqual(a.hostid, self.host)
        self.assertEqual(a.alias, "alias")


###############################################################################
class test_Links(TestCase):
    """Test Links"""

    def setUp(self):
        clearAKcache()
        self.host = Host(hostname="host")
        self.host.save()
        self.l1 = Links(hostid=self.host, url="http://localhost", tag="here")
        self.l1.save()
        self.l2 = Links(hostid=self.host, url="https://example.com", tag="there")
        self.l2.save()

    ###########################################################################
    def tearDown(self):
        self.l1.delete()
        self.l2.delete()
        self.host.delete()

    ###########################################################################
    def test_link(self):
        ls = Links.objects.all()
        self.assertEqual(len(ls), 2)
        self.assertEqual(ls[0].hostid, self.host)


###############################################################################
class test_parseQualifiers(TestCase):
    def setUp(self):
        clearAKcache()
        self.key = AllowedKey(key="kpq", validtype=1)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()

    ###########################################################################
    def test_singles(self):
        self.assertEqual(parseQualifiers(["kpq!=value"]), [(Qualifier.UNEQUAL, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq.ne.value"]), [(Qualifier.UNEQUAL, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq=value"]), [(Qualifier.EQUAL, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq.eq.value"]), [(Qualifier.EQUAL, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq<value"]), [(Qualifier.LESS_THAN, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq.lt.value"]), [(Qualifier.LESS_THAN, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq>value"]), [(Qualifier.GREATER_THAN, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq.gt.value"]), [(Qualifier.GREATER_THAN, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq~value"]), [(Qualifier.CONTAINS, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq.ss.value"]), [(Qualifier.CONTAINS, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq%value"]), [(Qualifier.NOT_CONTAINS, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq.ns.value"]), [(Qualifier.NOT_CONTAINS, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq@value"]), [(Qualifier.APPROX, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq.ap.value"]), [(Qualifier.APPROX, "kpq", "value")])
        self.assertEqual(parseQualifiers(["kpq.undef"]), [(Qualifier.UNDEF, "kpq", "")])
        self.assertEqual(parseQualifiers(["kpq.unset"]), [(Qualifier.UNDEF, "kpq", "")])
        self.assertEqual(parseQualifiers(["kpq.def"]), [(Qualifier.DEF, "kpq", "")])
        self.assertEqual(parseQualifiers(["kpq.set"]), [(Qualifier.DEF, "kpq", "")])
        self.assertEqual(parseQualifiers(["kpq.leneq.1"]), [(Qualifier.LEN_EQ, "kpq", "1")])
        self.assertEqual(parseQualifiers(["kpq.lenlt.2"]), [(Qualifier.LEN_LT, "kpq", "2")])
        self.assertEqual(parseQualifiers(["kpq.lengt.3"]), [(Qualifier.LEN_GT, "kpq", "3")])
        self.assertEqual(parseQualifiers(["HOST.hostre"]), [(Qualifier.HOST_RE, "host", "")])
        self.assertEqual(parseQualifiers(["HOST"]), [(Qualifier.HOST, None, "host")])
        self.assertEqual(parseQualifiers([]), [])

    ###########################################################################
    def test_hostmatch(self):
        host = Host(hostname="hosta.lt.example.com")
        host.save()
        self.assertEqual(
            parseQualifiers(["hosta.lt.example.com"]),
            [(Qualifier.HOST, None, "hosta.lt.example.com")],
        )
        host.delete()
        with self.assertRaises(HostinfoException):
            parseQualifiers(["hostb.lt.example.com"])

    ###########################################################################
    def test_series(self):
        self.assertEqual(
            parseQualifiers(["kpq!=value", "kpq.def", "kpq@value"]),
            [
                (Qualifier.UNEQUAL, "kpq", "value"),
                (Qualifier.DEF, "kpq", ""),
                (Qualifier.APPROX, "kpq", "value"),
            ],
        )

    ###########################################################################
    def test_badkey(self):
        with self.assertRaises(HostinfoException):
            parseQualifiers(["badkey=value"])


###############################################################################
class test_getMatches(TestCase):
    # The use of set's in the test cases is to make sure that the order
    # of the results is not an issue
    def setUp(self):
        clearAKcache()
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.host = Host(hostname="hostgma")
        self.host.save()

        self.host2 = Host(hostname="hostgmb")
        self.host2.save()

        self.singlekey = AllowedKey(key="single", validtype=1)
        self.singlekey.save()
        addKeytoHost(host="hostgma", key="single", value="100")

        self.numberkey = AllowedKey(key="number", validtype=1, numericFlag=True)
        self.numberkey.save()
        addKeytoHost(host="hostgma", key="number", value="100")
        addKeytoHost(host="hostgmb", key="number", value="2")

        self.listkey = AllowedKey(key="list", validtype=2)
        self.listkey.save()
        addKeytoHost(host="hostgma", key="list", value="alpha")
        addKeytoHost(host="hostgma", key="list", value="beta", appendFlag=True)
        addKeytoHost(host="hostgmb", key="list", value="alpha")

        self.datekey = AllowedKey(key="date", validtype=3)
        self.datekey.save()
        addKeytoHost(host="hostgma", key="date", value="2012/12/25")

    ###########################################################################
    def tearDown(self):
        self.numberkey.delete()
        self.singlekey.delete()
        self.listkey.delete()
        self.datekey.delete()
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_leneq(self):
        self.assertEqual(getMatches([(Qualifier.LEN_EQ, "list", "2")]), [self.host.id])

    ###########################################################################
    def test_lengt(self):
        self.assertEqual(getMatches([(Qualifier.LEN_GT, "list", "3")]), [])

    ###########################################################################
    def test_lenlt(self):
        self.assertCountEqual(getMatches([(Qualifier.LEN_LT, "list", "2")]), [self.host.id, self.host2.id])

    ###########################################################################
    def test_badlenlt(self):
        with self.assertRaises(HostinfoException) as cm:
            getMatches([(Qualifier.LEN_LT, "list", "foo")])
        self.assertEqual(cm.exception.msg, "Length must be an integer, not foo")

    ###########################################################################
    def test_equals(self):
        self.assertEqual(getMatches([(Qualifier.EQUAL, "single", "100")]), [self.host.id])
        self.assertEqual(set(getMatches([(Qualifier.EQUAL, "list", "alpha")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.EQUAL, "list", "beta")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.EQUAL, "list", "gamma")]), [])
        self.assertEqual(getMatches([(Qualifier.EQUAL, "date", "2012-12-25")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.EQUAL, "date", "2012/12/25")]), [])
        self.assertEqual(getMatches([(Qualifier.EQUAL, "date", "2012/12/26")]), [])
        self.assertEqual(getMatches([(Qualifier.EQUAL, "number", "2.0")]), [self.host2.id])
        try:
            getMatches([(Qualifier.EQUAL, "number", "five")]),
        except Exception:  # pragma: no cover
            self.fail("Non-numeric value for numeric key in equal")

    ###########################################################################
    def test_unequals(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEqual(getMatches([(Qualifier.UNEQUAL, "single", "100")]), [self.host2.id])
        self.assertEqual(getMatches([(Qualifier.UNEQUAL, "list", "alpha")]), [])
        self.assertEqual(getMatches([(Qualifier.UNEQUAL, "list", "beta")]), [self.host2.id])
        self.assertEqual(
            set(getMatches([(Qualifier.UNEQUAL, "list", "gamma")])),
            {self.host.id, self.host2.id},
        )
        self.assertEqual(getMatches([(Qualifier.UNEQUAL, "date", "2012-12-25")]), [self.host2.id])
        self.assertEqual(
            set(getMatches([(Qualifier.UNEQUAL, "date", "2012-12-26")])),
            {self.host.id, self.host2.id},
        )
        self.assertEqual(set(getMatches([(Qualifier.UNEQUAL, "number", "100.0")])), {self.host2.id})
        try:
            getMatches([(Qualifier.UNEQUAL, "number", "string")])
        except Exception:  # pragma: no cover
            self.fail("Non-numeric value for numeric key in unequal")

    ###########################################################################
    def test_greaterthan(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25, number=100
        # hostB: list=[alpha], number=2
        self.assertEqual(getMatches([(Qualifier.GREATER_THAN, "single", "99")]), [])
        self.assertEqual(getMatches([(Qualifier.GREATER_THAN, "single", "101")]), [])
        self.assertEqual(set(getMatches([(Qualifier.GREATER_THAN, "list", "aaaaa")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.GREATER_THAN, "list", "zzzzz")]), [])
        self.assertEqual(getMatches([(Qualifier.GREATER_THAN, "date", "2012-12-24")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.GREATER_THAN, "date", "2012-12-26")]), [])
        self.assertEqual(getMatches([(Qualifier.GREATER_THAN, "number", "10")]), [self.host.id])
        try:
            getMatches([(Qualifier.GREATER_THAN, "number", "hello")]),
        except Exception:  # pragma: no cover
            self.fail("Non-numeric value for numeric key in greaterthan")

    ###########################################################################
    def test_lessthan(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25, number=100
        # hostB: list=[alpha], number=2
        self.assertEqual(getMatches([(Qualifier.LESS_THAN, "single", "99")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.LESS_THAN, "single", "101")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.LESS_THAN, "list", "aaaaa")]), [])
        self.assertEqual(set(getMatches([(Qualifier.LESS_THAN, "list", "zzzzz")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.LESS_THAN, "date", "2012-12-24")]), [])
        self.assertEqual(getMatches([(Qualifier.LESS_THAN, "date", "2012-12-26")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.LESS_THAN, "number", "90")]), [self.host2.id])
        try:
            getMatches([(Qualifier.LESS_THAN, "number", "goodbye")]),
        except Exception:  # pragma: no cover
            self.fail("Non-numeric value for numeric key in lessthan")

    ###########################################################################
    def test_contains(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEqual(getMatches([(Qualifier.CONTAINS, "single", "0")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.CONTAINS, "single", "9")]), [])
        self.assertEqual(set(getMatches([(Qualifier.CONTAINS, "list", "alp")])), {self.host.id, self.host2.id})
        self.assertEqual(set(getMatches([(Qualifier.CONTAINS, "list", "alpha")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.CONTAINS, "list", "betan")]), [])
        self.assertEqual(getMatches([(Qualifier.CONTAINS, "date", "2012")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.CONTAINS, "date", "-13-")]), [])

    ###########################################################################
    def test_notcontains(self):
        self.assertEqual(getMatches([(Qualifier.NOT_CONTAINS, "single", "0")]), [self.host2.id])
        self.assertEqual(set(getMatches([(Qualifier.NOT_CONTAINS, "single", "9")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.NOT_CONTAINS, "list", "alp")]), [])
        self.assertEqual(getMatches([(Qualifier.NOT_CONTAINS, "list", "alpha")]), [])
        self.assertEqual(set(getMatches([(Qualifier.NOT_CONTAINS, "list", "betan")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.NOT_CONTAINS, "date", "2012")]), [self.host2.id])
        self.assertEqual(set(getMatches([(Qualifier.NOT_CONTAINS, "date", "-13-")])), {self.host.id, self.host2.id})

    ###########################################################################
    def test_approx(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEqual(set(getMatches([(Qualifier.APPROX, "list", "alhpa")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.APPROX, "list", "beta")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.APPROX, "list", "betan")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.APPROX, "date", "2012/12/26")]), [])
        self.assertEqual(getMatches([(Qualifier.APPROX, "single", "101")]), [self.host.id])
        self.assertEqual(getMatches([(Qualifier.APPROX, "single", "99")]), [])

    ###########################################################################
    def test_undef(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEqual(getMatches([(Qualifier.UNDEF, "single", "")]), [self.host2.id])
        self.assertEqual(getMatches([(Qualifier.UNDEF, "list", "")]), [])
        self.assertEqual(getMatches([(Qualifier.UNDEF, "date", "")]), [self.host2.id])

    ###########################################################################
    def test_def(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEqual(getMatches([(Qualifier.DEF, "single", "")]), [self.host.id])
        self.assertEqual(set(getMatches([(Qualifier.DEF, "list", "")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.DEF, "date", "")]), [self.host.id])

    ###########################################################################
    def test_hostre(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEqual(set(getMatches([(Qualifier.HOST_RE, "host", "")])), {self.host.id, self.host2.id})
        self.assertEqual(getMatches([(Qualifier.HOST_RE, "host2", "")]), [])

    ###########################################################################
    def test_host(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEqual(getMatches([(Qualifier.HOST, None, "host")]), [])
        self.assertEqual(getMatches([(Qualifier.HOST, None, "foo")]), [])


###############################################################################
class test_getHost(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.h1 = Host(hostname="h1")
        self.h1.save()
        self.al = HostAlias(hostid=self.h1, alias="a1")
        self.al.save()

    ###########################################################################
    def tearDown(self):
        self.al.delete()
        self.h1.delete()

    ###########################################################################
    def test_getbyhost(self):
        """Test getting a host that exists"""
        h = getHost("h1")
        self.assertEqual(h, self.h1)

    ###########################################################################
    def test_getbyalias(self):
        """Test getting a host via an alias"""
        h = getHost("a1")
        self.assertEqual(h, self.h1)

    ###########################################################################
    def test_nohost(self):
        """Test getting a host that doesn't exist"""
        h = getHost("a2")
        self.assertEqual(h, None)


###############################################################################
class test_getAK(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.ak = AllowedKey(key="ak_checkkey")
        self.ak.save()

    ###########################################################################
    def tearDown(self):
        self.ak.delete()

    ###########################################################################
    def test_checkexists(self):
        rc = getAK("ak_checkkey")
        self.assertTrue(rc)

    ###########################################################################
    def test_checknoexists(self):
        with self.assertRaises(HostinfoException) as cm:
            getAK("ak_badkey")
        self.assertEqual(cm.exception.msg, "Must use an existing key, not ak_badkey")


###############################################################################
class test_checkHost(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.h = Host(hostname="test_check_host")
        self.h.save()

    ###########################################################################
    def tearDown(self):
        self.h.delete()

    ###########################################################################
    def test_hostexists(self):
        rv = checkHost("test_check_host")
        self.assertTrue(rv)

    ###########################################################################
    def test_hostnotexists(self):
        rv = checkHost("badhost")
        self.assertFalse(rv)


###############################################################################
class test_hostviewrepr(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.key1 = AllowedKey(key="hvrkey1", validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key="hvrkey2", validtype=1)
        self.key2.save()
        self.host = Host(hostname="hvrhost1")
        self.host.save()
        self.host2 = Host(hostname="hvrhost2")
        self.host2.save()
        self.kv1 = KeyValue(hostid=self.host, keyid=self.key1, value="foo")
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host, keyid=self.key2, value="bar")
        self.kv2.save()

    ###########################################################################
    def tearDown(self):
        self.kv1.delete()
        self.key1.delete()
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_view(self):
        """Test a simple hostview repr"""
        ans = hostviewrepr("hvrhost1")
        self.assertEqual(ans, [("hvrkey1", [self.kv1]), ("hvrkey2", [self.kv2])])

    ###########################################################################
    def test_empty(self):
        """Test a hostview of an empty host"""
        ans = hostviewrepr("hvrhost2")
        self.assertEqual(ans, [])

    ###########################################################################
    def test_printers(self):
        """Test a hostview specifying what to print"""
        ans = hostviewrepr("hvrhost1", printers=["hvrkey1"])
        self.assertEqual(ans, [("hvrkey1", [self.kv1])])

    ###########################################################################
    def test_printer_with_missing(self):
        """hostviewrepr printing a host without that print value"""
        kv = KeyValue(hostid=self.host2, keyid=self.key1, value="baz")
        kv.save()
        ans = hostviewrepr("hvrhost2", printers=["hvrkey2", "hvrkey1"])
        self.assertEqual(ans, [("hvrkey2", []), ("hvrkey1", [kv])])
        kv.delete()


###############################################################################
class test_getHostMergeKeyData(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.host1 = Host(hostname="hmkdhost1")
        self.host1.save()
        self.host2 = Host(hostname="hmkdhost2")
        self.host2.save()
        self.key1 = AllowedKey(key="hmkdkey1", validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key="hmkdkey2", validtype=2)
        self.key2.save()
        self.kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value="foo")
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host2, keyid=self.key1, value="bar")
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.host1, keyid=self.key2, value="alpha")
        self.kv3.save()
        self.kv4 = KeyValue(hostid=self.host1, keyid=self.key2, value="beta")
        self.kv4.save()

    ###########################################################################
    def tearDown(self):
        self.kv1.delete()
        self.kv2.delete()
        self.kv3.delete()
        self.kv4.delete()
        self.host1.delete()
        self.host2.delete()
        self.key1.delete()
        self.key2.delete()

    ###########################################################################
    def test_hmkd(self):
        k = getHostMergeKeyData(self.host1, self.host2)
        self.assertEqual(k[0], ("hmkdkey1", {"src": ["foo"], "dst": ["bar"]}))
        self.assertEqual(sorted(k[1][1]["src"]), sorted(["alpha", "beta"]))
        self.assertEqual(k[1][1]["dst"], [])


###############################################################################
class test_orderhostlist(TestCase):
    def setUp(self):
        clearAKcache()
        self.key1 = AllowedKey(key="ohlkey1")
        self.key1.save()
        self.key2 = AllowedKey(key="ohlkey2", validtype=2)
        self.key2.save()
        self.key3 = AllowedKey(key="ohlkey3", numericFlag=True)
        self.key3.save()
        self.hosts = []
        self.kvals = []
        counts = ["1", "9", "10", "20", "100"]
        for h in ("a", "b", "c", "d", "e"):
            t = Host(hostname=h)
            t.save()
            self.hosts.append(t)
            kv = KeyValue(hostid=t, keyid=self.key1, value=h)
            kv.save()
            self.kvals.append(kv)
            kv = KeyValue(hostid=t, keyid=self.key2, value=f"{h}1")
            kv.save()
            self.kvals.append(kv)
            kv = KeyValue(hostid=t, keyid=self.key2, value="2")
            kv.save()
            self.kvals.append(kv)
            kv = KeyValue(hostid=t, keyid=self.key3, value=counts.pop(0))
            kv.save()
            self.kvals.append(kv)

    ###########################################################################
    def tearDown(self):
        for k in self.kvals:
            k.delete()
        for h in self.hosts:
            h.delete()
        self.key1.delete()
        self.key2.delete()
        self.key3.delete()

    ###########################################################################
    def test_order(self):
        out = orderHostList(self.hosts, "ohlkey1")
        self.hosts.sort(key=lambda x: x.hostname)
        self.assertEqual(out, self.hosts)

    ###########################################################################
    def test_numeric_order(self):
        out = orderHostList(self.hosts, "ohlkey3")
        self.hosts.sort(key=lambda x: x.hostname)
        self.assertEqual(out, self.hosts)

    ###########################################################################
    def test_reverse(self):
        out = orderHostList(self.hosts, "-ohlkey1")
        self.hosts.sort(key=lambda x: x.hostname, reverse=True)
        self.assertEqual(out, self.hosts)

    ###########################################################################
    def test_noval(self):
        """Output will be in hash order as all will sort equally"""
        with self.assertRaises(HostinfoException) as cm:
            orderHostList(self.hosts, "badkey")
        self.assertEqual(cm.exception.msg, "Must use an existing key, not badkey")

    ###########################################################################
    def test_list(self):
        out = orderHostList(self.hosts, "ohlkey2")
        self.assertEqual(out, self.hosts)


###############################################################################
class test_calcKeylistVals(TestCase):
    def setUp(self):
        clearAKcache()
        self.key1 = AllowedKey(key="ckvkey1", validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key="ckvkey2", validtype=1)
        self.key2.save()
        self.host1 = Host(hostname="ckvhost1")
        self.host1.save()
        self.host2 = Host(hostname="ckvhost2")
        self.host2.save()
        self.kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value="foo")
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host1, keyid=self.key2, value="bar")
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.host2, keyid=self.key2, value="baz")
        self.kv3.save()

    def tearDown(self):
        self.kv3.delete()
        self.kv2.delete()
        self.kv1.delete()
        self.host2.delete()
        self.host1.delete()
        self.key2.delete()
        self.key1.delete()

    def test_conditional(self):
        qualifiers = parseQualifiers(["ckvkey1.undefined"])
        matches = getMatches(qualifiers)
        d = calcKeylistVals("ckvkey2", matches)
        self.assertEqual(d["key"], "ckvkey2")
        self.assertEqual(d["numdef"], 1)
        self.assertEqual(d["numundef"], 0)
        self.assertEqual(d["pctdef"], 100.0)
        self.assertEqual(d["pctundef"], 0.0)
        self.assertEqual(d["total"], 1)
        self.assertEqual(d["numvals"], 1)
        self.assertEqual(d["vallist"], [("baz", 1, 100.0)])

    def test_another_key(self):
        d = calcKeylistVals("ckvkey1")
        self.assertEqual(d["key"], "ckvkey1")
        self.assertEqual(d["numdef"], 1)
        self.assertEqual(d["numundef"], 1)
        self.assertEqual(d["pctdef"], 50.0)
        self.assertEqual(d["pctundef"], 50.0)
        self.assertEqual(d["total"], 2)
        self.assertEqual(d["numvals"], 1)
        self.assertEqual(d["vallist"], [("foo", 1, 100.0)])

    def test_simple_key(self):
        d = calcKeylistVals("ckvkey2")
        self.assertEqual(d["key"], "ckvkey2")
        self.assertEqual(d["numdef"], 2)
        self.assertEqual(d["numundef"], 0)
        self.assertEqual(d["pctdef"], 100.0)
        self.assertEqual(d["pctundef"], 0.0)
        self.assertEqual(d["total"], 2)
        self.assertEqual(d["numvals"], 2)
        self.assertEqual(d["vallist"], [("bar", 1, 50.0), ("baz", 1, 50.0)])

    def test_bad_key(self):
        with self.assertRaises(HostinfoException):
            calcKeylistVals("badkey")


###############################################################################
class test_hostData(TestCase):
    def setUp(self):
        clearAKcache()
        self.key1 = AllowedKey(key="hdfkey1", validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key="hdfkey2", validtype=1)
        self.key2.save()
        self.host1 = Host(hostname="hdfhost1")
        self.host1.save()
        self.host2 = Host(hostname="hdfhost2")
        self.host2.save()
        self.host3 = Host(hostname="hdfhost3")
        self.host3.save()
        self.kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value="foo")
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host1, keyid=self.key2, value="bar")
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.host3, keyid=self.key2, value="baz")
        self.kv3.save()

    def tearDown(self):
        self.kv3.delete()
        self.kv2.delete()
        self.kv1.delete()
        self.host3.delete()
        self.host2.delete()
        self.host1.delete()
        self.key2.delete()
        self.key1.delete()

    def test_noargs(self):
        result = hostData("fred")
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["criteria"], "")
        self.assertEqual(result["title"], "")
        self.assertEqual(result["csvavailable"], "/hostinfo/csv/")
        self.assertEqual(result["options"], "")
        self.assertEqual(result["order"], None)
        self.assertEqual(result["printers"], [])
        self.assertEqual(result["user"], "fred")
        self.assertEqual(result["hostlist"][0]["hostname"], "hdfhost1")
        self.assertEqual(result["hostlist"][1]["hostname"], "hdfhost2")
        self.assertEqual(result["hostlist"][2]["hostname"], "hdfhost3")

    def test_double_criteria(self):
        result = hostData("fred", criteria=["hdfkey1.defined", "hdfhost1.hostre"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["criteria"], "hdfkey1.defined/hdfhost1.hostre")
        self.assertEqual(result["title"], "hdfkey1.defined AND hdfhost1.hostre")
        self.assertEqual(result["csvavailable"], "/hostinfo/csv/hdfkey1.defined/hdfhost1.hostre")
        self.assertEqual(result["options"], "")
        self.assertEqual(result["order"], None)
        self.assertEqual(result["printers"], [])
        self.assertEqual(result["user"], "fred")
        self.assertEqual(result["hostlist"][0]["hostname"], "hdfhost1")
        self.assertEqual(
            result["hostlist"][0]["hostview"],
            [("hdfkey1", [self.kv1]), ("hdfkey2", [self.kv2])],
        )

    def test_single_criteria(self):
        result = hostData("fred", criteria=["hdfkey1.defined"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["criteria"], "hdfkey1.defined")
        self.assertEqual(result["title"], "hdfkey1.defined")
        self.assertEqual(result["csvavailable"], "/hostinfo/csv/hdfkey1.defined")
        self.assertEqual(result["options"], "")
        self.assertEqual(result["order"], None)
        self.assertEqual(result["printers"], [])
        self.assertEqual(result["user"], "fred")
        self.assertEqual(result["hostlist"][0]["hostname"], "hdfhost1")

    def test_printers(self):
        result = hostData("fred", criteria=["hdfkey2.defined"], printers=["hdfkey2"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["criteria"], "hdfkey2.defined")
        self.assertEqual(result["title"], "hdfkey2.defined")
        self.assertEqual(result["csvavailable"], "/hostinfo/csv/hdfkey2.defined")
        self.assertEqual(result["options"], "")
        self.assertEqual(result["order"], None)
        self.assertEqual(result["printers"], ["hdfkey2"])
        self.assertEqual(result["user"], "fred")
        self.assertEqual(result["hostlist"][0]["hostview"], [("hdfkey2", [self.kv2])])
        self.assertEqual(result["hostlist"][1]["hostview"], [("hdfkey2", [self.kv3])])

    def test_order(self):
        host1 = Host(hostname="hdfhost4")
        host1.save()
        kv1 = KeyValue(hostid=host1, keyid=self.key1, value="alpha")
        kv1.save()
        host2 = Host(hostname="hdfhost5")
        host2.save()
        kv2 = KeyValue(hostid=host2, keyid=self.key1, value="zomega")
        kv2.save()

        result = hostData("fred", criteria=["hdfkey1.defined"], order="hdfkey1")
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["criteria"], "hdfkey1.defined")
        self.assertEqual(result["title"], "hdfkey1.defined")
        self.assertEqual(result["csvavailable"], "/hostinfo/csv/hdfkey1.defined")
        self.assertEqual(result["options"], "")
        self.assertEqual(result["order"], "hdfkey1")
        self.assertEqual(result["printers"], [])
        self.assertEqual(result["user"], "fred")
        self.assertEqual(result["hostlist"][0]["hostname"], "hdfhost4")
        self.assertEqual(result["hostlist"][1]["hostname"], "hdfhost1")
        self.assertEqual(result["hostlist"][2]["hostname"], "hdfhost5")
        kv1.delete()
        kv2.delete()
        host1.delete()
        host2.delete()


###############################################################################
class test_version(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_version(self):
        response = self.client.get("/_version")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertTrue(len(ans["version"]) > 1)


# EOF
