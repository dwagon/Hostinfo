# Test rig for hostinfo

# Written by Dougal Scott <dougal.scott@gmail.com>

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

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
import sys
import time
import StringIO

from .models import HostinfoException, ReadonlyValueException, RestrictedValueException
from .models import Host, HostAlias, AllowedKey, KeyValue, RestrictedValue, Links

from .models import validateDate
from .models import parseQualifiers, getMatches
from .models import getHost, getAkCache, checkHost
from .models import checkKey, addKeytoHost, run_from_cmdline

from .views import getHostMergeKeyData, hostviewrepr
# from .views import mergeKey, doHostMerging
# from .views import doHostMergeChoose, doHostMerge, doHostRenameChoose, doHostRename
# from .views import doHostCreateChoose, doHostCreate, doHostEditChoose, doHostEdit
# from .views import handlePost, doHostEditChanges, getLinks, getWebLinks, getWikiLinks
# from .views import getHostDetails, doHostSummary, doHost, doHostDataFormat, doHostlist
# from .views import doHostcmp, orderHostList, doHostwikiTable, doHostwiki, doCsvreport
from .views import orderHostList
# from .views import getHostList, csvDump, index
# from .views import doRestrValList, doKeylist


###############################################################################
class test_SingleKey(TestCase):
    """ Test operations on a single values key """
    def setUp(self):
        self.host = Host(hostname='host')
        self.host.save()
        self.key = AllowedKey(key='single', validtype=1)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def checkValue(self, host, key):
        keyid = checkKey(key)
        hostid = getHost(host)
        kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
        return kv[0].value

    ###########################################################################
    def test_adds(self):
        """Test adding a simple value """
        addKeytoHost(host='host', key='single', value='a')
        self.assertEquals(self.checkValue('host', 'single'), 'a')

    ###########################################################################
    def test_readonly(self):
        """ Test modifications to readonly keys """
        self.rokey = AllowedKey(key='ro', validtype=1, readonlyFlag=True)
        self.rokey.save()
        with self.assertRaises(ReadonlyValueException):
            addKeytoHost(host='host', key='ro', value='b')
        addKeytoHost(host='host', key='ro', value='a', readonlyFlag=True)
        self.assertEquals(self.checkValue('host', 'ro'), 'a')
        self.rokey.delete()

    ###########################################################################
    def test_addtwice(self):
        """ Test adding the same value again """
        addKeytoHost(host='host', key='single', value='a')
        addKeytoHost(host='host', key='single', value='a')
        self.assertEquals(self.checkValue('host', 'single'), 'a')

    ###########################################################################
    def test_changevalue(self):
        """ Add a value without override"""
        addKeytoHost(host='host', key='single', value='a')
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='host', key='single', value='b')
        self.assertEquals(self.checkValue('host', 'single'), 'a')

    ###########################################################################
    def test_override(self):
        """ Add a value with override"""
        addKeytoHost(host='host', key='single', value='a')
        addKeytoHost(host='host', key='single', value='b', updateFlag=True)
        self.assertEquals(self.checkValue('host', 'single'), 'b')

    ###########################################################################
    def test_nohost(self):
        """ Test adding to a host that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='hostnot', key='single', value='b')

    ###########################################################################
    def test_append(self):
        """ Test to make sure we can't append
        """
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='host', key='single', value='a', appendFlag=True)

    ###########################################################################
    def test_badkey(self):
        """ Test adding to a key that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='host', key='fake', value='b')


###############################################################################
class test_ListKey(TestCase):
    """ Test operations on a list of values key """
    def setUp(self):
        self.host = Host(hostname='host')
        self.host.save()
        self.key = AllowedKey(key='list', validtype=2)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def checkValue(self, host, key):
        keyid = checkKey(key)
        hostid = getHost(host)
        kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
        ans = [k.value for k in kv]
        if len(ans) == 1:
            return ans[0]
        else:
            return sorted(ans)

    ###########################################################################
    def test_adds(self):
        """Test adding a simple value """
        addKeytoHost(host='host', key='list', value='a')
        self.assertEquals(self.checkValue('host', 'list'), 'a')

    ###########################################################################
    def test_readonly(self):
        """ Test modifications to readonly keys """
        self.rokey = AllowedKey(key='ro', validtype=1, readonlyFlag=True)
        self.rokey.save()
        addKeytoHost(host='host', key='ro', value='a', readonlyFlag=True)
        addKeytoHost(host='host', key='ro', value='a')
        self.assertEquals(self.checkValue('host', 'ro'), 'a')
        self.rokey.delete()

    ###########################################################################
    def test_addtwice(self):
        """ Test adding the same value again """
        addKeytoHost(host='host', key='list', value='a')
        addKeytoHost(host='host', key='list', value='a')
        self.assertEquals(self.checkValue('host', 'list'), 'a')

    ###########################################################################
    def test_changevalue(self):
        """ Add a value without override"""
        addKeytoHost(host='host', key='list', value='a')
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='host', key='list', value='b')
        self.assertEquals(self.checkValue('host', 'list'), 'a')

    ###########################################################################
    def test_override(self):
        """ Add a value with override"""
        addKeytoHost(host='host', key='list', value='a')
        addKeytoHost(host='host', key='list', value='b', updateFlag=True)
        self.assertEquals(self.checkValue('host', 'list'), 'b')

    ###########################################################################
    def test_nohost(self):
        """ Test adding to a host that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='hostnot', key='list', value='b')

    ###########################################################################
    def test_append(self):
        """ Test to make sure we can append
        """
        addKeytoHost(host='host', key='list', value='a')
        addKeytoHost(host='host', key='list', value='b', appendFlag=True)
        self.assertEquals(self.checkValue('host', 'list'), ['a', 'b'])

    ###########################################################################
    def test_badkey(self):
        """ Test adding to a key that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='host', key='fake', value='b')


###############################################################################
class test_Restricted(TestCase):
    """ Test operations on a restricted key
    """
    def setUp(self):
        self.host = Host(hostname='host')
        self.host.save()
        self.key = AllowedKey(key='restr', validtype=1, restrictedFlag=True)
        self.key.save()
        self.rv = RestrictedValue(keyid=self.key, value='allowed')
        self.rv.save()

    ###########################################################################
    def tearDown(self):
        self.rv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_adds(self):
        """ Test that we can add a key of the appropriate value
        and that it raises an exception if we add the wrong value
        """
        with self.assertRaises(RestrictedValueException):
            addKeytoHost(host='host', key='restr', value='forbidden')
        addKeytoHost(host='host', key='restr', value='allowed')


###############################################################################
class test_DateKey(TestCase):
    """ Test operations on a date based key
    """
    def setUp(self):
        self.host = Host(hostname='host')
        self.host.save()
        self.key = AllowedKey(key='date', validtype=3)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def checkValue(self, host, key):
        keyid = checkKey(key)
        hostid = getHost(host)
        kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
        return kv[0].value

    ###########################################################################
    def test_adds(self):
        """Test adding a simple value """
        addKeytoHost(host='host', key='date', value='2012-12-31')
        self.assertEquals(self.checkValue('host', 'date'), '2012-12-31')


###############################################################################
class test_DateValidator(TestCase):
    """ Test validateDate()
    """

    ###########################################################################
    def test_formats(self):
        self.assertEquals(validateDate("2012-12-31"), "2012-12-31")
        self.assertEquals(validateDate("31/12/2012"), "2012-12-31")
        self.assertEquals(validateDate("31/12/12"), "2012-12-31")
        self.assertEquals(validateDate("2012/12/31"), "2012-12-31")

    ###########################################################################
    def test_today(self):
        now = time.strftime("%Y-%m-%d")
        self.assertEquals(validateDate("now"), now)
        self.assertEquals(validateDate("today"), now)


###############################################################################
class test_HostAlias(TestCase):
    """ Test HostAlias class
    """
    def setUp(self):
        self.host = Host(hostname='host')
        self.host.save()
        self.alias = HostAlias(hostid=self.host, alias='alias')
        self.alias.save()

    ###########################################################################
    def tearDown(self):
        self.alias.delete()
        self.host.delete()

    def test_alias(self):
        a = HostAlias.objects.all()[0]
        self.assertEquals(a.hostid, self.host)
        self.assertEquals(a.alias, 'alias')


###############################################################################
class test_Links(TestCase):
    """ Test Links
    """
    def setUp(self):
        self.host = Host(hostname='host')
        self.host.save()
        self.l1 = Links(hostid=self.host, url='http://localhost', tag='here')
        self.l1.save()
        self.l2 = Links(hostid=self.host, url='https://example.com', tag='there')
        self.l2.save()

    ###########################################################################
    def tearDown(self):
        self.l1.delete()
        self.l2.delete()
        self.host.delete()

    ###########################################################################
    def test_link(self):
        ls = Links.objects.all()
        self.assertEquals(len(ls), 2)
        self.assertEquals(ls[0].hostid, self.host)


###############################################################################
class test_parseQualifiers(TestCase):
    def setUp(self):
        self.key = AllowedKey(key='kpq', validtype=1)
        self.key.save()
        getAkCache()

    ###########################################################################
    def tearDown(self):
        self.key.delete()

    ###########################################################################
    def test_singles(self):
        self.assertEquals(parseQualifiers(['kpq!=value']), [('unequal', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq.ne.value']), [('unequal', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq=value']), [('equal', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq.eq.value']), [('equal', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq<value']), [('lessthan', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq.lt.value']), [('lessthan', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq>value']), [('greaterthan', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq.gt.value']), [('greaterthan', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq~value']), [('contains', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq.ss.value']), [('contains', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq%value']), [('notcontains', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq.ns.value']), [('notcontains', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq@value']), [('approx', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq.ap.value']), [('approx', 'kpq', 'value')])
        self.assertEquals(parseQualifiers(['kpq.undef']), [('undef', 'kpq', '')])
        self.assertEquals(parseQualifiers(['kpq.unset']), [('undef', 'kpq', '')])
        self.assertEquals(parseQualifiers(['kpq.def']), [('def', 'kpq', '')])
        self.assertEquals(parseQualifiers(['kpq.set']), [('def', 'kpq', '')])
        self.assertEquals(parseQualifiers(['HOST.hostre']), [('hostre', 'host', '')])
        self.assertEquals(parseQualifiers(['HOST']), [('host', None, 'host')])
        self.assertEquals(parseQualifiers([]), [])

    ###########################################################################
    def test_series(self):
        self.assertEquals(
            parseQualifiers(['kpq!=value', 'kpq.def', 'kpq@value']),
            [('unequal', 'kpq', 'value'), ('def', 'kpq', ''), ('approx', 'kpq', 'value')]
            )

    ###########################################################################
    def test_badkey(self):
        with self.assertRaises(HostinfoException):
            parseQualifiers(['badkey=value'])


###############################################################################
class test_getMatches(TestCase):
    # The use of set's in the test cases is to make sure that the order
    # of the results is not an issue
    def setUp(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.host = Host(hostname='hostgma')
        self.host.save()

        self.host2 = Host(hostname='hostgmb')
        self.host2.save()

        self.singlekey = AllowedKey(key='single', validtype=1)
        self.singlekey.save()
        addKeytoHost(host='hostgma', key='single', value='100')

        self.listkey = AllowedKey(key='list', validtype=2)
        self.listkey.save()
        addKeytoHost(host='hostgma', key='list', value='alpha')
        addKeytoHost(host='hostgma', key='list', value='beta', appendFlag=True)
        addKeytoHost(host='hostgmb', key='list', value='alpha')

        self.datekey = AllowedKey(key='date', validtype=3)
        self.datekey.save()
        addKeytoHost(host='hostgma', key='date', value='2012/12/25')
        getAkCache()

    ###########################################################################
    def tearDown(self):
        self.singlekey.delete()
        self.listkey.delete()
        self.datekey.delete()
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_equals(self):
        self.assertEquals(
            getMatches([('equal', 'single', '100')]),
            [self.host.id]
            )
        self.assertEquals(
            set(getMatches([('equal', 'list', 'alpha')])),
            set([self.host.id, self.host2.id])
            )
        self.assertEquals(
            getMatches([('equal', 'list', 'beta')]),
            [self.host.id]
            )
        self.assertEquals(
            getMatches([('equal', 'list', 'gamma')]),
            []
            )
        self.assertEquals(
            getMatches([('equal', 'date', '2012-12-25')]),
            [self.host.id]
            )
        self.assertEquals(
            getMatches([('equal', 'date', '2012/12/25')]),
            []
            )
        self.assertEquals(
            getMatches([('equal', 'date', '2012/12/26')]),
            []
            )

    ###########################################################################
    def test_unequals(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(
            getMatches([('unequal', 'single', '100')]),
            [self.host2.id]
            )
        self.assertEquals(
            getMatches([('unequal', 'list', 'alpha')]),
            []
            )
        self.assertEquals(
            getMatches([('unequal', 'list', 'beta')]),
            [self.host2.id]
            )
        self.assertEquals(
            set(getMatches([('unequal', 'list', 'gamma')])),
            set([self.host.id,  self.host2.id])
            )
        self.assertEquals(
            getMatches([('unequal', 'date', '2012-12-25')]),
            [self.host2.id]
            )
        self.assertEquals(
            set(getMatches([('unequal', 'date', '2012-12-26')])),
            set([self.host.id, self.host2.id])
            )

    ###########################################################################
    def test_greaterthan(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(getMatches([('greaterthan', 'single', '99')]), [])
        self.assertEquals(getMatches([('greaterthan', 'single', '101')]), [])
        self.assertEquals(
            set(getMatches([('greaterthan', 'list', 'aaaaa')])),
            set([self.host.id,  self.host2.id])
            )
        self.assertEquals(getMatches([('greaterthan', 'list', 'zzzzz')]), [])
        self.assertEquals(
            getMatches([('greaterthan', 'date', '2012-12-24')]),
            [self.host.id]
            )
        self.assertEquals(
            getMatches([('greaterthan', 'date', '2012-12-26')]),
            []
            )

    ###########################################################################
    def test_lessthan(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(
            getMatches([('lessthan', 'single', '99')]),
            [self.host.id]
            )
        self.assertEquals(
            getMatches([('lessthan', 'single', '101')]),
            [self.host.id]
            )
        self.assertEquals(
            getMatches([('lessthan', 'list', 'aaaaa')]),
            []
            )
        self.assertEquals(
            set(getMatches([('lessthan', 'list', 'zzzzz')])),
            set([self.host.id,  self.host2.id])
            )
        self.assertEquals(
            getMatches([('lessthan', 'date', '2012-12-24')]),
            []
            )
        self.assertEquals(
            getMatches([('lessthan', 'date', '2012-12-26')]),
            [self.host.id]
            )

    ###########################################################################
    def test_contains(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(
            getMatches([('contains', 'single', '0')]),
            [self.host.id]
            )
        self.assertEquals(
            getMatches([('contains', 'single', '9')]),
            []
            )
        self.assertEquals(
            set(getMatches([('contains', 'list', 'alp')])),
            set([self.host.id, self.host2.id])
            )
        self.assertEquals(
            set(getMatches([('contains', 'list', 'alpha')])),
            set([self.host.id, self.host2.id])
            )
        self.assertEquals(
            getMatches([('contains', 'list', 'betan')]),
            []
            )
        self.assertEquals(
            getMatches([('contains', 'date', '2012')]),
            [self.host.id]
            )
        self.assertEquals(
            getMatches([('contains', 'date', '-13-')]),
            []
            )

    ###########################################################################
    def test_notcontains(self):
        self.assertEquals(getMatches([('notcontains', 'single', '0')]), [self.host2.id])
        self.assertEquals(set(getMatches([('notcontains', 'single', '9')])), set([self.host.id, self.host2.id]))
        self.assertEquals(getMatches([('notcontains', 'list', 'alp')]), [])
        self.assertEquals(getMatches([('notcontains', 'list', 'alpha')]), [])
        self.assertEquals(set(getMatches([('notcontains', 'list', 'betan')])), set([self.host.id, self.host2.id]))
        self.assertEquals(getMatches([('notcontains', 'date', '2012')]), [self.host2.id])
        self.assertEquals(set(getMatches([('notcontains', 'date', '-13-')])), set([self.host.id, self.host2.id]))

    ###########################################################################
    def test_approx(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(set(getMatches([('approx', 'list', 'alhpa')])), set([self.host.id, self.host2.id]))
        self.assertEquals(getMatches([('approx', 'list', 'beta')]), [self.host.id])
        self.assertEquals(getMatches([('approx', 'list', 'betan')]), [self.host.id])
        self.assertEquals(getMatches([('approx', 'date', '2012/12/26')]), [])
        self.assertEquals(getMatches([('approx', 'single', '101')]), [self.host.id])
        self.assertEquals(getMatches([('approx', 'single', '99')]), [])

    ###########################################################################
    def test_undef(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(getMatches([('undef', 'single', '')]), [self.host2.id])
        self.assertEquals(getMatches([('undef', 'list', '')]), [])
        self.assertEquals(getMatches([('undef', 'date', '')]), [self.host2.id])

    ###########################################################################
    def test_def(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(getMatches([('def', 'single', '')]), [self.host.id])
        self.assertEquals(set(getMatches([('def', 'list', '')])), set([self.host.id, self.host2.id]))
        self.assertEquals(getMatches([('def', 'date', '')]), [self.host.id])

    ###########################################################################
    def test_hostre(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(set(getMatches([('hostre', 'host', '')])), set([self.host.id, self.host2.id]))
        self.assertEquals(getMatches([('hostre', 'host2', '')]), [])

    ###########################################################################
    def test_host(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.assertEquals(getMatches([('host', None, 'host')]), [])
        self.assertEquals(getMatches([('host', None, 'foo')]), [])


###############################################################################
class test_getHost(TestCase):
    ###########################################################################
    def setUp(self):
        self.h1 = Host(hostname='h1')
        self.h1.save()
        self.al = HostAlias(hostid=self.h1, alias='a1')
        self.al.save()

    ###########################################################################
    def tearDown(self):
        self.al.delete()
        self.h1.delete()

    ###########################################################################
    def test_getbyhost(self):
        """ Test getting a host that exists"""
        h = getHost('h1')
        self.assertEquals(h, self.h1)

    ###########################################################################
    def test_getbyalias(self):
        """ Test getting a host via an alias"""
        h = getHost('a1')
        self.assertEquals(h, self.h1)

    ###########################################################################
    def test_nohost(self):
        """ Test getting a host that doesn't exist"""
        h = getHost('a2')
        self.assertEquals(h, None)


###############################################################################
class test_checkKey(TestCase):
    ###########################################################################
    def setUp(self):
        self.ak = AllowedKey(key='ak_checkkey')
        self.ak.save()

    ###########################################################################
    def tearDown(self):
        self.ak.delete()

    ###########################################################################
    def test_checkexists(self):
        rc = checkKey('ak_checkkey')
        self.assertTrue(rc)

    ###########################################################################
    def test_checknoexists(self):
        with self.assertRaises(HostinfoException) as cm:
            rc = checkKey('ak_badkey')
            print rc
        self.assertEquals(cm.exception.msg, "Must use an existing key, not ak_badkey")


###############################################################################
class test_checkHost(TestCase):
    ###########################################################################
    def setUp(self):
        self.h = Host(hostname='test_check_host')
        self.h.save()

    ###########################################################################
    def tearDown(self):
        self.h.delete()

    ###########################################################################
    def test_hostexists(self):
        rv = checkHost('test_check_host')
        self.assertTrue(rv)

    ###########################################################################
    def test_hostnotexists(self):
        rv = checkHost('badhost')
        self.assertFalse(rv)


###############################################################################
class test_cmd_hostinfo(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.h1 = Host(hostname='h1', origin='me')
        self.h1.save()
        self.h2 = Host(hostname='h2', origin='you')
        self.h2.save()
        self.ak1 = AllowedKey(key='ak1')
        self.ak1.save()
        self.ak2 = AllowedKey(key='ak2')
        self.ak2.save()
        self.kv1 = KeyValue(hostid=self.h1, keyid=self.ak1, value='kv1', origin='foo')
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.h2, keyid=self.ak1, value='kv2', origin='bar')
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.h1, keyid=self.ak2, value='kv3', origin='baz')
        self.kv3.save()
        self.alias = HostAlias(hostid=self.h1, alias='halias')
        self.alias.save()

    ###########################################################################
    def tearDown(self):
        self.alias.delete()
        self.kv1.delete()
        self.kv2.delete()
        self.kv3.delete()
        self.h1.delete()
        self.h2.delete()
        self.ak1.delete()
        self.ak2.delete()

    ###########################################################################
    def test_explicit_host(self):
        th1 = Host(hostname='h4.lt.com', origin='me')
        namespace = self.parser.parse_args(['--host', 'h4.lt.com'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('h4.lt.com\n', 0))
        th1.delete()

    ###########################################################################
    def test_hostinfo(self):
        namespace = self.parser.parse_args([])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('h1\nh2\n', 0))

    ###########################################################################
    def testnomatches(self):
        namespace = self.parser.parse_args(['h3'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('', 1))

    ###########################################################################
    def testnormal_p(self):
        namespace = self.parser.parse_args(['-p', 'ak1'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('h1\tak1=kv1\nh2\tak1=kv2\n', 0))

    ###########################################################################
    def testnormal_missingp(self):
        namespace = self.parser.parse_args(['-p', 'ak1', '-p', 'ak2'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('h1\tak1=kv1\tak2=kv3\nh2\tak1=kv2\tak2=\n', 0))

    ###########################################################################
    def testnormal_times(self):
        import time
        t = time.strftime("%Y-%m-%d", time.localtime())
        namespace = self.parser.parse_args(['-p', 'ak1', '--times'])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output,
            ('h1\t[Created: %s Modified: %s]\tak1=kv1[Created: %s, Modified: %s]\nh2\t[Created: %s Modified: %s]\tak1=kv2[Created: %s, Modified: %s]\n' % (t, t, t, t, t, t, t, t), 0))

    ###########################################################################
    def testnormal_origin(self):
        namespace = self.parser.parse_args(['-p', 'ak1', '--origin'])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output,
            ('h1\t[Origin: me]\tak1=kv1[Origin: foo]\nh2\t[Origin: you]\tak1=kv2[Origin: bar]\n', 0))

    ###########################################################################
    def testbadkey(self):
        namespace = self.parser.parse_args(['-p', 'badkey'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No key called badkey")

    ###########################################################################
    def test_hostinfo_csv(self):
        namespace = self.parser.parse_args(['--csv'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('hostname,\nh1\nh2\n', 0))

    ###########################################################################
    def test_hostinfo_csvp(self):
        namespace = self.parser.parse_args(['--csv', '-p', 'ak1', '-p', 'ak2'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('hostname,ak1,ak2\nh1,"kv1","kv3"\nh2,"kv2",\n', 0))

    ###########################################################################
    def test_hostinfo_csvsep(self):
        namespace = self.parser.parse_args(['-p', 'ak1', '-p', 'ak2', '--csv', '--sep', '#'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('hostname#ak1#ak2\nh1#"kv1"#"kv3"\nh2#"kv2"#\n', 0))

    ###########################################################################
    def test_hostinfo_showall(self):
        namespace = self.parser.parse_args(['--showall'])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output,
            ('h1\n    ak1: kv1            \n    ak2: kv3            \nh2\n    ak1: kv2            \n', 0)
            )

    ###########################################################################
    def test_hostinfo_xml(self):
        """ Test outputting hosts only in xml mode """
        namespace = self.parser.parse_args(['--xml'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn('<hostname>h1</hostname>', output[0])
        self.assertIn('<hostname>h2</hostname>', output[0])
        self.assertNotIn('confitem', output[0])
        # TODO: Replace with something that pulls the whole xml apart

    ###########################################################################
    def test_hostinfo_hostsep(self):
        namespace = self.parser.parse_args(['--hsep', ':'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('h1:h2\n', 0))

    ###########################################################################
    def test_hostinfo_xml_p(self):
        namespace = self.parser.parse_args(['--xml', '-p', 'ak1'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn('<hostname>h1</hostname>', output[0])
        self.assertIn('<hostname>h2</hostname>', output[0])
        self.assertIn('<confitem key="ak1">kv1</confitem>', output[0])
        self.assertIn('<confitem key="ak1">kv2</confitem>', output[0])
        self.assertIn('<name>ak1</name>', output[0])
        self.assertIn('<type>single</type>', output[0])
        # TODO: Replace with something that pulls the whole xml apart

    ###########################################################################
    def test_hostinfo_xml_showall(self):
        namespace = self.parser.parse_args(['--xml', '--showall'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn('<name>ak1</name>', output[0])
        self.assertIn('<name>ak2</name>', output[0])
        self.assertIn('<confitem key="ak1">kv1</confitem>', output[0])
        self.assertIn('<confitem key="ak2">kv3</confitem>', output[0])
        # TODO: Replace with something that pulls the whole xml apart

    ###########################################################################
    def test_hostinfo_xml_aliases(self):
        namespace = self.parser.parse_args(['--xml', '--aliases', '--showall'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn('<alias>halias</alias>', output[0])
        self.assertIn('<name>ak1</name>', output[0])
        self.assertIn('<name>ak2</name>', output[0])
        self.assertIn('<confitem key="ak1">kv1</confitem>', output[0])
        self.assertIn('<confitem key="ak2">kv3</confitem>', output[0])
        # TODO: Replace with something that pulls the whole xml apart

    ###########################################################################
    def test_hostinfo_valuereport(self):
        namespace = self.parser.parse_args(['--valuereport', 'ak1'])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output[0],
            'ak1 set: 2 100.00%\nak1 unset: 0 0.00%\n\nkv1 1 50.00%\nkv2 1 50.00%\n')
        self.assertEquals(output[1], 0)

        # No matches
        namespace = self.parser.parse_args(['--valuereport', 'ak1', 'ak2=novalue'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[0], '')
        self.assertEquals(output[1], 1)


###############################################################################
class test_cmd_addalias(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_addalias import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_hostnotexists(self):
        """ Test creating an alias of a host that doesn't exist
        """
        namespace = self.parser.parse_args(['host', 'alias'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host host doesn't exist")

    ###########################################################################
    def test_aliasexists(self):
        """ Test creating an alias that already exists
        """
        host = Host(hostname='host')
        host.save()
        alias = Host(hostname='alias')
        alias.save()
        namespace = self.parser.parse_args(['host', 'alias'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host alias already exists")
        host.delete()
        alias.delete()

    ###########################################################################
    def test_creation(self):
        """ Make sure than an alias is created
        """
        host = Host(hostname='host')
        host.save()
        namespace = self.parser.parse_args(['--origin', 'test', 'host', 'alias'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        alias = HostAlias.objects.get(hostid=host)
        self.assertEquals(alias.origin, 'test')
        self.assertEquals(alias.alias, 'alias')
        alias.delete()
        host.delete()


###############################################################################
class test_cmd_addhost(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_addhost import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_alreadyexists(self):
        host = Host(hostname='host')
        host.save()
        namespace = self.parser.parse_args(['host'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host host already exists")
        host.delete()
        h = Host.objects.all()
        self.assertEquals(len(h), 0)

    ###########################################################################
    def test_creation(self):
        namespace = self.parser.parse_args(['--origin', 'test', 'host'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        host = Host.objects.get(hostname='host')
        self.assertEquals(host.hostname, 'host')
        self.assertEquals(host.origin, 'test')
        host.delete()

    ###########################################################################
    def test_lowercase(self):
        namespace = self.parser.parse_args(['HOST'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        host = Host.objects.get(hostname='host')
        self.assertEquals(host.hostname, 'host')
        host.delete()

    ###########################################################################
    def test_badname(self):
        namespace = self.parser.parse_args(['--', '-badhost'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg,
            "Host begins with a forbidden character ('-') - not adding")
        h = Host.objects.all()
        self.assertEquals(len(h), 0)


###############################################################################
class test_cmd_addkey(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_addkey import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_alreadyExists(self):
        ak = AllowedKey(key='key_addkey_t1')
        ak.save()
        namespace = self.parser.parse_args(['key_addkey_t1'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Key already exists with that name: key_addkey_t1")
        ak.delete()

    ###########################################################################
    def test_addRestricted(self):
        namespace = self.parser.parse_args(['--restricted', 'key_addkey_t2'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t2')
        self.assertEquals(key.restrictedFlag, True)
        self.assertEquals(key.readonlyFlag, False)
        self.assertEquals(key.auditFlag, True)
        self.assertEquals(key.get_validtype_display(), 'single')
        self.assertEquals(key.desc, '')
        key.delete()

    ###########################################################################
    def test_addReadonly(self):
        namespace = self.parser.parse_args(['--readonly', 'key_addkey_t3'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t3')
        self.assertEquals(key.restrictedFlag, False)
        self.assertEquals(key.readonlyFlag, True)
        self.assertEquals(key.auditFlag, True)
        key.delete()

    ###########################################################################
    def test_addSingle(self):
        namespace = self.parser.parse_args(['key_addkey_t4', 'single'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t4')
        self.assertEquals(key.auditFlag, True)
        self.assertEquals(key.get_validtype_display(), 'single')
        key.delete()

    ###########################################################################
    def test_addList(self):
        namespace = self.parser.parse_args(['key_addkey_t5', 'list'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t5')
        self.assertEquals(key.get_validtype_display(), 'list')
        key.delete()

    ###########################################################################
    def test_addDate(self):
        namespace = self.parser.parse_args(['key_addkey_t6', 'date'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t6')
        self.assertEquals(key.get_validtype_display(), 'date')
        key.delete()

    ###########################################################################
    def test_withDescription(self):
        namespace = self.parser.parse_args(
            ['key_addkey_t7', 'single', 'this', 'is', 'a', 'description'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t7')
        self.assertEquals(key.desc, 'this is a description')
        key.delete()

    ###########################################################################
    def test_withExplicitKeyType(self):
        namespace = self.parser.parse_args(['--keytype', 'list', 'key_addkey_t8'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t8')
        key.delete()

    ###########################################################################
    def test_withExplicitKeyTypeAndDesc(self):
        namespace = self.parser.parse_args(
            ['--keytype', 'date', 'key_addkey_t9', 'this', 'is', 'a', 'description'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t9')
        self.assertEquals(key.get_validtype_display(), 'date')
        key.delete()

    ###########################################################################
    def test_lowercase(self):
        namespace = self.parser.parse_args(['KEY_ADDKEY_T10'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t10')
        key.delete()

    ###########################################################################
    def test_addnoaudit(self):
        namespace = self.parser.parse_args(['--noaudit', 'key_addkey_t11'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key='key_addkey_t11')
        self.assertEquals(key.auditFlag, False)
        key.delete()

    ###########################################################################
    def test_unknowntype(self):
        namespace = self.parser.parse_args(['key_addkey_t12', 'invalid', 'description'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg,
            "Unknown type invalid - should be one of single,list,date")


###############################################################################
class test_cmd_addrestrictedvalue(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_addrestrictedvalue import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.key = AllowedKey(key='restr', validtype=1, restrictedFlag=True)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()

    ###########################################################################
    def test_addvalue(self):
        namespace = self.parser.parse_args(['restr=value'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        rv = RestrictedValue.objects.filter()[0]
        self.assertEquals(rv.value, 'value')
        self.assertEquals(rv.keyid, self.key)

    ###########################################################################
    def test_missingkey(self):
        namespace = self.parser.parse_args(['key2=value'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No key key2 found")

    ###########################################################################
    def test_unrestricted(self):
        self.key2 = AllowedKey(key='unrestr', validtype=1, restrictedFlag=False)
        self.key2.save()
        namespace = self.parser.parse_args(['unrestr=value'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Key unrestr isn't a restrictedvalue key")
        self.key2.delete()

    ###########################################################################
    def test_alreadyexists(self):
        self.rv = RestrictedValue(keyid=self.key, value='value')
        self.rv.save()
        namespace = self.parser.parse_args(['restr=value'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Already a key restr=value in the restrictedvalue list")
        self.rv.delete()

    ###########################################################################
    def test_wrongformat(self):
        namespace = self.parser.parse_args(['key value'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must be specified in key=value format")


###############################################################################
class test_cmd_addvalue(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_addvalue import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname='testhost')
        self.host.save()

    ###########################################################################
    def tearDown(self):
        self.host.delete()

    ###########################################################################
    def test_addvalue(self):
        """ Test normal operation of adding a new key/value pair"""
        key = AllowedKey(key='key_addvalue_t1', validtype=1)
        key.save()
        namespace = self.parser.parse_args(['--origin', 'whence', 'key_addvalue_t1=VALUE', 'testhost'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        kv = KeyValue.objects.filter()[0]
        self.assertEquals(kv.hostid, self.host)
        self.assertEquals(kv.value, 'value')
        self.assertEquals(kv.origin, 'whence')
        key.delete()

    ###########################################################################
    def test_multiplehosts(self):
        key = AllowedKey(key='key_addvalue_t2', validtype=1)
        key.save()
        host2 = Host(hostname='testhost2')
        host2.save()
        namespace = self.parser.parse_args(['--origin', 'whence2', 'key_addvalue_t2=value2', 'testhost', 'testhost2'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        for h in (self.host, host2):
            kv = KeyValue.objects.filter(hostid=h)[0]
            self.assertEquals(kv.value, 'value2')
            self.assertEquals(kv.origin, 'whence2')
        key.delete()
        host2.delete()

    ###########################################################################
    def test_restrictedkey(self):
        """ Test that we can't add a non-allowed value to a restricted key
        Then test that we can add an allowed value to a restricted key
        """
        key = AllowedKey(key='rkey', validtype=1, restrictedFlag=True)
        key.save()
        rv = RestrictedValue(keyid=key, value='restrvalue')
        rv.save()

        namespace = self.parser.parse_args(['rkey=value', 'testhost'])
        with self.assertRaises(RestrictedValueException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Cannot add rkey=value to a restricted key")
        kv = KeyValue.objects.filter(keyid=key)
        self.assertEquals(len(kv), 0)

        namespace = self.parser.parse_args(['rkey=restrvalue', 'testhost'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        kv = KeyValue.objects.get(keyid=key)
        self.assertEquals(kv.value, 'restrvalue')

        rv.delete()
        key.delete()

    ###########################################################################
    def test_baddsyntax(self):
        """ Test that we can't add something that doesn't match key=value """
        namespace = self.parser.parse_args(['badvalue', 'testhost'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must be specified in key=value format")

    ###########################################################################
    def test_readonlykey(self):
        """ Test that we can't add a value to a readonly key without the correct option"""
        key = AllowedKey(key='rokey', validtype=1, readonlyFlag=True)
        key.save()
        namespace = self.parser.parse_args(['rokey=value', 'testhost'])
        with self.assertRaises(ReadonlyValueException):
            self.cmd.handle(namespace)
        kv = KeyValue.objects.filter(keyid=key)
        self.assertEqual(list(kv), [])

        # Now try with correct options
        namespace = self.parser.parse_args(['--readonlyupdate', 'rokey=value', 'testhost'])
        self.cmd.handle(namespace)
        kv = KeyValue.objects.filter(keyid=key)
        self.assertEqual(kv[0].value, 'value')
        key.delete()

    ###########################################################################
    def test_missingkey(self):
        namespace = self.parser.parse_args(['mkey=value', 'testhost'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must use an existing key, not mkey")


###############################################################################
class test_cmd_deletealias(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_deletealias import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname='host')
        self.host.save()

    ###########################################################################
    def tearDown(self):
        self.host.delete()

    ###########################################################################
    def test_deletealias(self):
        """ Test deletion of an alias"""
        alias = HostAlias(hostid=self.host, alias='alias')
        alias.save()
        namespace = self.parser.parse_args(['alias'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        alias.delete()
        aliaslist = HostAlias.objects.all()
        self.assertEquals(len(aliaslist), 0)

    ###########################################################################
    def test_deletemissingalias(self):
        """ Test the attempted deletion of an alias that doesn't exist"""
        namespace = self.parser.parse_args(['badalias'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No alias called badalias")


###############################################################################
class test_cmd_deletehost(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_deletehost import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_nonlethal(self):
        """ Test that without --lethal it does nothing"""
        h = Host(hostname='test')
        h.save()
        namespace = self.parser.parse_args(['test'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Didn't do delete as no --lethal specified")
        hosts = Host.objects.all()
        self.assertEqual(len(hosts), 1)
        h.delete()

    ###########################################################################
    def test_deleterefers(self):
        """ Test that aliases and kv pairs get deleted as well """
        h = Host(hostname='test')
        h.save()
        a = HostAlias(hostid=h, alias='testalias')
        a.save()
        ak = AllowedKey(key='key_deletehost', validtype=1)
        ak.save()
        kv = KeyValue(hostid=h, keyid=ak, value='foo')
        kv.save()

        namespace = self.parser.parse_args(['--lethal', 'test'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))

        hosts = Host.objects.all()
        self.assertEqual(len(hosts), 0)
        kvs = KeyValue.objects.all()
        self.assertEqual(len(kvs), 0)
        aliases = HostAlias.objects.all()
        self.assertEqual(len(aliases), 0)
        h.delete()
        ak.delete()

    ###########################################################################
    def test_deletehost(self):
        """ Test the deletion of a host """
        h = Host(hostname='test')
        h.save()
        namespace = self.parser.parse_args(['--lethal', 'test'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        hosts = Host.objects.all()
        self.assertEqual(len(hosts), 0)
        h.delete()

    ###########################################################################
    def test_deletewronghost(self):
        """ Test the deletion of a host that doesn't exist"""
        namespace = self.parser.parse_args(['--lethal', 'test2'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host test2 doesn't exist")


###############################################################################
class test_cmd_deleterestrictedvalue(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_deleterestrictedvalue import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

        self.key = AllowedKey(key='restr', validtype=1, restrictedFlag=True)
        self.key.save()
        self.rv = RestrictedValue(keyid=self.key, value='allowed')
        self.rv.save()

    ###########################################################################
    def tearDown(self):
        self.rv.delete()
        self.key.delete()

    ###########################################################################
    def test_deleterestrval(self):
        """ Test the deletion of a restricted value """
        namespace = self.parser.parse_args(['restr=allowed'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        rv = RestrictedValue.objects.all()
        self.assertEquals(len(rv), 0)

    ###########################################################################
    def test_missingvalue(self):
        """ Test the deletion of a value that doesn't exist"""
        namespace = self.parser.parse_args(['restr=bad'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No key restr=bad in the restrictedvalue list")

    ###########################################################################
    def test_badkeyname(self):
        """ Test the deletion from a key that doesn't exist"""
        namespace = self.parser.parse_args(['bad=allowed'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No key bad=allowed in the restrictedvalue list")

    ###########################################################################
    def test_badkeytype(self):
        """ Test the deletion of a value from a non-restricted key"""
        k1 = AllowedKey(key='free', validtype=1, restrictedFlag=False)
        k1.save()
        namespace = self.parser.parse_args(['free=allowed'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No key free=allowed in the restrictedvalue list")
        k1.delete()

    ###########################################################################
    def test_badformat(self):
        """ Test specifying the args badly"""
        namespace = self.parser.parse_args(['foobar'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must be specified in key=value format")


###############################################################################
class test_cmd_deletevalue(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_deletevalue import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.h1 = Host(hostname='host_delval')
        self.h1.save()
        self.ak = AllowedKey(key='key_dv')
        self.ak.save()
        self.kv = KeyValue(hostid=self.h1, keyid=self.ak, value='deletevalue')
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.ak.delete()
        self.h1.delete()

    ###########################################################################
    def test_deletevalue(self):
        """ Test the deletion of a value"""
        namespace = self.parser.parse_args(['key_dv=deletevalue', 'host_delval'])
        output = self.cmd.handle(namespace)
        kvlist = KeyValue.objects.filter(hostid=self.h1)
        self.assertEquals(output, (None, 0))
        self.assertEquals(len(kvlist), 0)

    ###########################################################################
    def test_delete_novalue(self):
        """ Test the deletion of a value where the value isn't specified"""
        namespace = self.parser.parse_args(['key_dv', 'host_delval'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kvlist = KeyValue.objects.filter(hostid=self.h1)
        self.assertEquals(len(kvlist), 0)

    ###########################################################################
    def test_badhost(self):
        """ Test deleting from a host that doesn't exists"""
        namespace = self.parser.parse_args(['key_dv=deletevalue', 'badhost'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Unknown host: badhost")
        kvlist = KeyValue.objects.filter(hostid=self.h1)
        self.assertEquals(len(kvlist), 1)

    ###########################################################################
    def test_readonlydeletion(self):
        """ Test deleting a readonly value """
        """ Test deleting a value from a host that doesn't have it"""
        ak2 = AllowedKey(key='key2_dv', readonlyFlag=True)
        ak2.save()
        kv2 = KeyValue(hostid=self.h1, keyid=ak2, value='deletevalue')
        kv2.save(readonlychange=True)
        namespace = self.parser.parse_args(['key2_dv=deletevalue', 'host_delval'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Cannot delete a readonly value")
        kv2.delete(readonlychange=True)
        ak2.delete()

    ###########################################################################
    def test_badkey(self):
        """ Test deleting a value from a key that doesn't exist """
        namespace = self.parser.parse_args(['badkey_dv=deletevalue', 'host_delval'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must use an existing key, not badkey_dv")

    ###########################################################################
    def test_deletebadkey(self):
        """ Test deleting a value from a host that doesn't have it"""
        ak = AllowedKey(key='key3_dv')
        ak.save()
        namespace = self.parser.parse_args(['key3_dv=deletevalue', 'host_delval'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host host_delval doesn't have key key3_dv")
        ak.delete()


###############################################################################
class test_cmd_history(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_history import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.t = time.strftime("%Y-%m-%d", time.localtime())

    ###########################################################################
    def test_badhost(self):
        namespace = self.parser.parse_args(['badhost'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('', 1))

    ###########################################################################
    def test_origin(self):
        host = Host(hostname='host_history_o', origin='host_origin')
        host.save()
        ak = AllowedKey(key='key4_dv')
        ak.save()
        kv = KeyValue(keyid=ak, hostid=host, value='historic', origin='kv_origin')
        kv.save()
        namespace = self.parser.parse_args(['-o', 'host_history_o'])
        output = self.cmd.handle(namespace)
        self.assertTrue('origin host_origin' in output[0])
        self.assertTrue('origin kv_origin' in output[0])
        self.assertTrue(self.t in output[0])
        kv.delete()
        ak.delete()
        host.delete()

    ###########################################################################
    def test_actor(self):
        """ Make sure that we are saving the actor properly
        """
        host = Host(hostname='host_history_a')
        host.save()
        ak = AllowedKey(key='key5_dv')
        ak.save()
        kv = KeyValue(keyid=ak, hostid=host, value='historic')
        kv.save()
        namespace = self.parser.parse_args(['-a', 'host_history_a'])
        output = self.cmd.handle(namespace)
        self.assertTrue('using ' in output[0])
        self.assertTrue(sys.argv[0] in output[0])
        self.assertTrue(self.t in output[0])
        kv.delete()
        ak.delete()
        host.delete()

    ###########################################################################
    def test_hostadd(self):
        host = Host(hostname='host_history_ha')
        host.save()
        namespace = self.parser.parse_args(['host_history_ha'])
        output = self.cmd.handle(namespace)
        self.assertTrue('added host_history_ha' in output[0])
        self.assertTrue(self.t in output[0])
        host.delete()

    ###########################################################################
    def test_valadd(self):
        host = Host(hostname='host_history_va')
        host.save()
        ak = AllowedKey(key='key3_dv')
        ak.save()
        kv = KeyValue(keyid=ak, hostid=host, value='historic')
        kv.save()
        namespace = self.parser.parse_args(['host_history_va'])
        output = self.cmd.handle(namespace)
        self.assertTrue('added host_history_va:key3_dv with historic' in output[0])
        self.assertTrue(self.t in output[0])
        kv.delete()
        ak.delete()
        host.delete()

    ###########################################################################
    def test_valdelete(self):
        host = Host(hostname='host_history_vd')
        host.save()
        ak = AllowedKey(key='key4_dv')
        ak.save()
        kv = KeyValue(keyid=ak, hostid=host, value='historic')
        kv.save()
        kv.delete()
        namespace = self.parser.parse_args(['host_history_vd'])
        output = self.cmd.handle(namespace)
        self.assertTrue('deleted key4_dv:historic on host_history_vd' in output[0])
        self.assertTrue(self.t in output[0])
        ak.delete()
        host.delete()

    ###########################################################################
    def test_noaudit(self):
        host = Host(hostname='host_history_na')
        host.save()
        ak1 = AllowedKey(key='key5_na', auditFlag=False)
        ak1.save()
        ak2 = AllowedKey(key='key6_na')
        ak2.save()
        kv = KeyValue(keyid=ak1, hostid=host, value='historic')
        kv.save()
        kv2 = KeyValue(keyid=ak2, hostid=host, value='historic')
        kv2.save()
        namespace = self.parser.parse_args(['host_history_na'])
        output = self.cmd.handle(namespace)
        self.assertFalse('added key5_na:historic on host_history_na' in output[0])
        self.assertTrue('added key6_na:historic on host_history_na' in output[0])
        kv.delete()
        kv2.delete()
        ak1.delete()
        ak2.delete()
        host.delete()


###############################################################################
class test_cmd_import(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_import import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_badfile(self):
        namespace = self.parser.parse_args(['badfile'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "File badfile doesn't exist")


###############################################################################
class test_cmd_listalias(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_listalias import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname='host')
        self.host.save()
        self.alias1 = HostAlias(hostid=self.host, alias='foo')
        self.alias1.save()
        self.alias2 = HostAlias(hostid=self.host, alias='bar')
        self.alias2.save()

    ###########################################################################
    def tearDown(self):
        self.alias1.delete()
        self.alias2.delete()
        self.host.delete()

    ###########################################################################
    def test_listhost(self):
        """ Test listing the aliases of a host"""
        namespace = self.parser.parse_args(['host'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("host\nbar\nfoo\n", 0))

    ###########################################################################
    def test_listnoaliases(self):
        """ Test list aliases where there are none """
        h = Host(hostname='test2')
        h.save()
        namespace = self.parser.parse_args(['test2'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('test2\n', 1))
        h.delete()

    ###########################################################################
    def test_listbadhost(self):
        """ Test list aliases of a host that doesn't exist"""
        namespace = self.parser.parse_args(['badhost'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host badhost doesn't exist")

    ###########################################################################
    def test_listall(self):
        """ Test listing all aliases """
        namespace = self.parser.parse_args(['--all'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('foo host\nbar host\n', 0))

    ###########################################################################
    def test_listnone(self):
        """ Test listing neither all or a host """
        namespace = self.parser.parse_args([])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('foo host\nbar host\n', 0))


###############################################################################
class test_cmd_listrestrictedvalue(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_listrestrictedvalue import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.key = AllowedKey(key='restr', validtype=1, restrictedFlag=True)
        self.key.save()
        self.rv = RestrictedValue(keyid=self.key, value='allowed')
        self.rv.save()

    ###########################################################################
    def tearDown(self):
        self.rv.delete()
        self.key.delete()

    ###########################################################################
    def test_list(self):
        """ Test normal behaviour"""
        namespace = self.parser.parse_args(['restr'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('allowed\n', 0))

    ###########################################################################
    def test_badkey(self):
        """ Specfied key doesn't exist"""
        namespace = self.parser.parse_args(['nokey'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No key nokey found")


###############################################################################
class test_cmd_mergehost(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_mergehost import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host1 = Host(hostname='mrghost1')
        self.host1.save()
        self.host2 = Host(hostname='mrghost2')
        self.host2.save()
        self.key1 = AllowedKey(key='mergesingle', validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key='mergelist', validtype=2)
        self.key2.save()
        self.stderr = sys.stderr
        sys.stderr = StringIO.StringIO()

    ###########################################################################
    def tearDown(self):
        self.key1.delete()
        self.key2.delete()
        self.host1.delete()
        self.host2.delete()
        sys.stderr = self.stderr

    ###########################################################################
    def test_mergehost_single(self):
        namespace = self.parser.parse_args(['--src', 'mrghost1', '--dst', 'mrghost2'])
        kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value='val1')
        kv1.save()
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key1)
        self.assertEqual(kv[0].value, 'val1')

    ###########################################################################
    def test_mergehost_list(self):
        """ Merge two hosts with overlapping lists """
        namespace = self.parser.parse_args(['--src', 'mrghost1', '--dst', 'mrghost2'])
        addKeytoHost(host='mrghost1', key='mergelist', value='a')
        addKeytoHost(host='mrghost1', key='mergelist', value='b', appendFlag=True)
        addKeytoHost(host='mrghost1', key='mergelist', value='c', appendFlag=True)
        addKeytoHost(host='mrghost2', key='mergelist', value='c')
        addKeytoHost(host='mrghost2', key='mergelist', value='d', appendFlag=True)
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key2)
        vals = sorted([k.value for k in kv])
        self.assertEqual(vals, ['a', 'b', 'c', 'd'])

    ###########################################################################
    def test_merge_collide(self):
        """ Merge two hosts that have the same key set with a different value """
        namespace = self.parser.parse_args(['--src', 'mrghost1', '--dst', 'mrghost2'])
        kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value='val1')
        kv1.save()
        kv2 = KeyValue(hostid=self.host2, keyid=self.key1, value='val2')
        kv2.save()
        output = self.cmd.handle(namespace)
        errout = sys.stderr.getvalue()
        errmsgs = [
            "Collision: mergesingle src=val1 dst=val2",
            "To keep dst mrghost2 value val2: hostinfo_addvalue --update mergesingle='val2' mrghost1",
            "To keep src mrghost1 value val1: hostinfo_addvalue --update mergesingle='val1' mrghost2"
            ]
        for msg in errmsgs:
            self.assertIn(msg, errout)
        self.assertEquals(output, ("Failed to merge", 1))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key1)
        self.assertEqual(kv[0].value, 'val2')

    ###########################################################################
    def test_merge_collide_force(self):
        """ Force merge two hosts that have the same key set with a different value
        """
        namespace = self.parser.parse_args(['--force', '--src', 'mrghost1', '--dst', 'mrghost2'])
        kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value='val1')
        kv1.save()
        kv2 = KeyValue(hostid=self.host2, keyid=self.key1, value='val2')
        kv2.save()
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key1)
        self.assertEqual(kv[0].value, 'val2')

    ###########################################################################
    def test_merge_no_collide(self):
        """ Merge two hosts that have the same key set with the same value """
        namespace = self.parser.parse_args(['--src', 'mrghost1', '--dst', 'mrghost2'])
        kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value='vala')
        kv1.save()
        kv2 = KeyValue(hostid=self.host2, keyid=self.key1, value='vala')
        kv2.save()
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key1)
        self.assertEqual(kv[0].value, 'vala')

    ###########################################################################
    def test_merge_no_srchost(self):
        """ Attempt merge where srchost doesn't exist """
        namespace = self.parser.parse_args(['--src', 'badhost', '--dst', 'mrghost2'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Source host badhost doesn't exist")

    ###########################################################################
    def test_merge_no_dsthost(self):
        """ Attempt merge where dsthost doesn't exist """
        namespace = self.parser.parse_args(['--src', 'mrghost1', '--dst', 'badhost'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Destination host badhost doesn't exist")


###############################################################################
class test_cmd_renamehost(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_renamehost import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname='renhost')
        self.host.save()
        self.host2 = Host(hostname='renhost2')
        self.host2.save()

    ###########################################################################
    def tearDown(self):
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_renamehost(self):
        namespace = self.parser.parse_args(['--src', 'renhost', '--dst', 'newhost'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        hosts = Host.objects.filter(hostname='newhost')
        self.assertEquals(hosts[0], self.host)

    ###########################################################################
    def test_renamehbadost(self):
        namespace = self.parser.parse_args(['--src', 'renbadhost', '--dst', 'newhost'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "There is no host called renbadhost")

    ###########################################################################
    def test_renameexisting(self):
        namespace = self.parser.parse_args(['--src', 'renhost', '--dst', 'renhost2'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "A host already exists with the name renhost2")


###############################################################################
class test_cmd_replacevalue(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_replacevalue import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.key = AllowedKey(key='repval', validtype=1)
        self.key.save()
        self.host = Host(hostname='rephost')
        self.host.save()
        self.host2 = Host(hostname='rephost2')
        self.host2.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value='before')
        self.kv.save()
        self.kv2 = KeyValue(hostid=self.host2, keyid=self.key, value='before')
        self.kv2.save()
        self.stderr = sys.stderr
        sys.stderr = StringIO.StringIO()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.kv2.delete()
        self.key.delete()
        self.host.delete()
        self.host2.delete()
        sys.stderr = self.stderr

    ###########################################################################
    def test_replacevalue(self):
        namespace = self.parser.parse_args(['repval=before', 'after', 'rephost'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host, keyid=self.key)[0]
        self.assertEquals(kv.value, 'after')

    ###########################################################################
    def test_badvalue(self):
        namespace = self.parser.parse_args(['repval=notexists', 'newvalue', 'rephost'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host, keyid=self.key)[0]
        self.assertEquals(kv.value, 'before')

    ###########################################################################
    def test_badkey(self):
        namespace = self.parser.parse_args(['badkey=value', 'newvalue', 'rephost'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must use an existing key, not badkey")

    ###########################################################################
    def test_badexpr(self):
        namespace = self.parser.parse_args(['badexpr', 'nobody', 'cares'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must be in key=value format, not badexpr")

    ###########################################################################
    def test_nohosts(self):
        namespace = self.parser.parse_args(['repval=before', 'after'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must specify a list of hosts or the --all flag")

    ###########################################################################
    def test_all(self):
        namespace = self.parser.parse_args(['repval=before', 'after', '--all'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kvlist = KeyValue.objects.filter(keyid=self.key)
        for k in kvlist:
            self.assertEquals(k.value, 'after')

    ###########################################################################
    def test_kidding(self):
        """ Test that it doesn't actually do anything in kidding mode"""
        namespace = self.parser.parse_args(['-k', 'repval=before', 'after', 'rephost'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host, keyid=self.key)[0]
        self.assertEquals(kv.value, 'before')


###############################################################################
class test_cmd_showkey(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_showkey import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.key1 = AllowedKey(key='showkey1', validtype=1, desc='description', restrictedFlag=True)
        self.key1.save()
        self.key2 = AllowedKey(key='showkey2', validtype=2, desc='another description', readonlyFlag=True)
        self.key2.save()
        self.key3 = AllowedKey(key='showkey3', validtype=3, desc='')
        self.key3.save()

    ###########################################################################
    def tearDown(self):
        self.key1.delete()
        self.key2.delete()
        self.key3.delete()

    ###########################################################################
    def test_showkey(self):
        namespace = self.parser.parse_args([])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output,
            ('showkey1\tsingle\tdescription\t[KEY RESTRICTED]\nshowkey2\tlist\tanother description\t[KEY READ ONLY]\nshowkey3\tdate\t\n', 0)
            )

    ###########################################################################
    def test_showtype(self):
        namespace = self.parser.parse_args(['--type'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('showkey1\tsingle\nshowkey2\tlist\nshowkey3\tdate\n', 0))

    ###########################################################################
    def test_showkeylist(self):
        namespace = self.parser.parse_args(['showkey1'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('showkey1\tsingle\tdescription\t[KEY RESTRICTED]\n', 0))

    ###########################################################################
    def test_showbadkeylist(self):
        namespace = self.parser.parse_args(['badkey'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No keys to show")


###############################################################################
class test_cmd_undolog(TestCase):
    ###########################################################################
    def setUp(self):
        import argparse
        from commands.cmd_hostinfo_undolog import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_user(self):
        """ Test normal behaviour for a user"""
        namespace = self.parser.parse_args(['--user', 'foo'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('', 0))

    ###########################################################################
    def test_week(self):
        """ Test normal behaviour for a week"""
        namespace = self.parser.parse_args(['--week'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)

    ###########################################################################
    def test_days(self):
        """ Test normal behaviour for 5 days"""
        namespace = self.parser.parse_args(['--days', '5'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)

    ###########################################################################
    def test_undolog(self):
        """ Test normal behaviour"""
        namespace = self.parser.parse_args([])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)


###############################################################################
class test_run_from_cmdline(TestCase):
    ###########################################################################
    def setUp(self):
        self.oldargv = sys.argv
        self.stderr = sys.stderr
        sys.stderr = StringIO.StringIO()

    ###########################################################################
    def tearDown(self):
        sys.argv = self.oldargv
        sys.stderr = self.stderr

    ###########################################################################
    def test_run(self):
        sys.argv = ['hostinfo_listalias', ]
        run_from_cmdline()

    ###########################################################################
    def test_badrun(self):
        sys.argv[0] = 'notexists'
        rv = run_from_cmdline()
        self.assertEquals(rv, 255)
        errout = sys.stderr.getvalue()
        self.assertIn("No such hostinfo command notexists", errout)


###############################################################################
class test_url_hostmerge(TestCase):
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', '', 'passwd')
        self.user.save()
        self.host1 = Host(hostname='merge1')
        self.host1.save()
        self.host2 = Host(hostname='merge2')
        self.host2.save()
        self.key = AllowedKey(key='mergekey', validtype=1)
        self.key.save()
        self.kv = KeyValue(hostid=self.host1, keyid=self.key, value='foo')
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.user.delete()
        self.host1.delete()
        self.host2.delete()
        self.key.delete()

    ###########################################################################
    def test_merge_form(self):
        """ Ask for the host merge form """
        self.client.login(username='test', password='passwd')
        response = self.client.get('/hostinfo/hostmerge/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostmerge.template', 'host/base.html']
            )

    ###########################################################################
    def test_do_merge(self):
        """ Send answers to the host merge form
        """
        self.client.login(username='test', password='passwd')
        response = self.client.post(
            '/hostinfo/hostmerge/',
            {'_srchost': 'merge1', '_dsthost': 'merge2'},
            follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostmerge.template', 'host/base.html']
            )
        host = Host.objects.filter(hostname='merge1')
        sys.stderr.write("Fix merge test\n")
        return  # TODO
        self.assertEquals(len(host), 0)
        host = Host.objects.filter(hostname='merge2')
        self.assertEquals(len(host), 1)
        kv = KeyValue.objects.filter(hostid=self.host2, keyid=self.key)
        self.assertEquals(kv[0].value, 'foo')


###############################################################################
class test_url_hostrename(TestCase):
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', '', 'passwd')
        self.user.save()
        self.host = Host(hostname='urenamehost1')
        self.host.save()

    ###########################################################################
    def tearDown(self):
        self.user.delete()
        self.host.delete()

    ###########################################################################
    def test_do_rename(self):
        """ Send answers to the host rename form
        """
        self.client.login(username='test', password='passwd')
        response = self.client.post(
            '/hostinfo/hostrename/',
            {'srchost': 'urenamehost1', 'dsthost': 'urenamed'},
            follow=True)

        self.assertIn('urenamehost1 has been successfully renamed to urenamed', response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostrename.template', 'host/base.html']
            )
        host = Host.objects.filter(hostname='urenamehost1')
        self.assertEquals(len(host), 0)
        host = Host.objects.filter(hostname='urenamed')
        self.assertEquals(len(host), 1)

    ###########################################################################
    def test_blank_form(self):
        """ Ask for the host rename form """
        self.client.login(username='test', password='passwd')
        response = self.client.get('/hostinfo/hostrename/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostrename.template', 'host/base.html']
            )


###############################################################################
class test_url_index(TestCase):
    ###########################################################################
    def setUp(self):
        self.client = Client()

    ###########################################################################
    def tearDown(self):
        pass

    ###########################################################################
    def test_base(self):
        response = self.client.get('/hostinfo/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/index.template', 'host/base.html']
            )


###############################################################################
class test_url_handlePost(TestCase):
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.key = AllowedKey(key='postkey', validtype=1)
        self.key.save()
        self.host = Host(hostname='posthost')
        self.host.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value='foo')
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_hostname(self):
        response = self.client.post('/hostinfo/handlePost/', data={'hostname': 'posthost'})
        self.assertEquals(response.status_code, 302)
        response = self.client.post('/hostinfo/handlePost/', data={'hostname': 'posthost'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            sorted([t.name for t in response.templates]),
            ['host/base.html', 'host/host.template', 'host/showall.template']
            )


###############################################################################
class test_url_keylist(TestCase):
    """ Test views doKeylist function"""
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.key = AllowedKey(key='urlkey', validtype=1)
        self.key.save()
        self.host = Host(hostname='urlhost1')
        self.host.save()
        self.host2 = Host(hostname='urlhost2')
        self.host2.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value='foo')
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_withkey(self):
        response = self.client.get('/hostinfo/keylist/urlkey/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            sorted([t.name for t in response.templates]),
            ['host/base.html', 'host/keylist.template']
            )
        self.assertEquals(response.context['key'], 'urlkey')
        self.assertEquals(response.context['total'], 2)          # Number of hosts
        self.assertEquals(response.context['numkeys'], 1)        # Number of different values
        self.assertEquals(response.context['pctundef'], 50)      # % hosts with key not defined
        self.assertEquals(response.context['numundef'], 1)       # Num hosts with key not defined
        self.assertEquals(response.context['pctdef'], 50)        # % hosts with key defined
        self.assertEquals(response.context['numdef'], 1)         # Num hosts with key defined
        self.assertEquals(response.context['keylist'], [('foo', 1, 100)])    # Key, Value, Percentage

    ###########################################################################
    def test_badkey(self):
        response = self.client.get('/hostinfo/keylist/badkey/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            sorted([t.name for t in response.templates]),
            ['host/base.html', 'host/keylist.template']
            )
        self.assertEquals(response.context['key'], 'badkey')
        self.assertEquals(response.context['total'], 2)          # Number of hosts
        self.assertEquals(response.context['numkeys'], 0)        # Number of different values
        self.assertEquals(response.context['pctundef'], 100)      # % hosts with key not defined
        self.assertEquals(response.context['numundef'], 2)       # Num hosts with key not defined
        self.assertEquals(response.context['pctdef'], 0)        # % hosts with key defined
        self.assertEquals(response.context['numdef'], 0)         # Num hosts with key defined
        self.assertEquals(response.context['keylist'], [])    # Key, Value, Percentage


###############################################################################
class test_hostviewrepr(TestCase):
    ###########################################################################
    def setUp(self):
        self.key = AllowedKey(key='hvrkey', validtype=1)
        self.key.save()
        self.host = Host(hostname='hvrhost1')
        self.host.save()
        self.host2 = Host(hostname='hvrhost2')
        self.host2.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value='foo')
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_view(self):
        ans = hostviewrepr('hvrhost1')
        self.assertEquals(ans, [(u'hvrkey', [self.kv])])
        ans = hostviewrepr('hvrhost2')
        self.assertEquals(ans, [])


###############################################################################
class test_getHostMergeKeyData(TestCase):
    ###########################################################################
    def setUp(self):
        self.host1 = Host(hostname='hmkdhost1')
        self.host1.save()
        self.host2 = Host(hostname='hmkdhost2')
        self.host2.save()
        self.key1 = AllowedKey(key='hmkdkey1', validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key='hmkdkey2', validtype=2)
        self.key2.save()
        self.kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value='foo')
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host2, keyid=self.key1, value='bar')
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.host1, keyid=self.key2, value='alpha')
        self.kv3.save()
        self.kv4 = KeyValue(hostid=self.host1, keyid=self.key2, value='beta')
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
        self.assertEquals(k[0], ('hmkdkey1', {'src': ['foo'], 'dst': ['bar']}))
        self.assertEquals(
            sorted(k[1][1]['src']),
            sorted(['alpha', 'beta'])
            )
        self.assertEquals(k[1][1]['dst'], [])


###############################################################################
class test_url_rvlist(TestCase):
    """ Test doRestrValList function and /hostinfo/rvlist url
        (r'^rvlist/(?P<key>\S+)/$', 'doRestrValList'),
        (r'^rvlist/(?P<key>\S+)/(?P<mode>\S+)$', 'doRestrValList'),
        """
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.key = AllowedKey(key='rvlkey', validtype=1, restrictedFlag=True)
        self.key.save()
        self.rv1 = RestrictedValue(keyid=self.key, value='good')
        self.rv1.save()
        self.rv2 = RestrictedValue(keyid=self.key, value='better')
        self.rv2.save()
        self.rv3 = RestrictedValue(keyid=self.key, value='best')
        self.rv3.save()

    ###########################################################################
    def tearDown(self):
        self.rv3.delete()
        self.rv2.delete()
        self.rv1.delete()
        self.key.delete()

    ###########################################################################
    def test_rvlist(self):
        response = self.client.get('/hostinfo/rvlist/rvlkey/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/restrval.template', 'host/base.html']
            )
        self.assertEquals(response.context['key'], 'rvlkey')
        self.assertEquals(len(response.context['rvlist']), 3)
        self.assertTrue(self.rv1 in response.context['rvlist'])
        self.assertTrue(self.rv2 in response.context['rvlist'])

    ###########################################################################
    def test_rvlist_wiki(self):
        response = self.client.get('/hostinfo/rvlist/rvlkey/wiki')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals([t.name for t in response.templates], ['restrval.wiki'])
        self.assertEquals(response.context['key'], 'rvlkey')
        self.assertEquals(len(response.context['rvlist']), 3)
        self.assertTrue(self.rv1 in response.context['rvlist'])
        self.assertTrue(self.rv2 in response.context['rvlist'])
        self.assertTrue(self.rv3 in response.context['rvlist'])


###############################################################################
class test_url_host_summary(TestCase):
    # (r'^host_summary/(?P<hostname>.*)/(?P<format>\S+)$', 'doHostSummary'),
    # (r'^host_summary/(?P<hostname>.*)$', 'doHostSummary'),
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.host = Host(hostname='hosths')
        self.host.save()
        self.key = AllowedKey(key='hskey', validtype=2)
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host, keyid=self.key, value='kv1', origin='foo')
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host, keyid=self.key, value='kv2', origin='foo')
        self.kv2.save()
        self.al = HostAlias(hostid=self.host, alias='a1')
        self.al.save()
        self.link = Links(hostid=self.host, url='http://code.google.com/p/hostinfo', tag='hslink')
        self.link.save()

    ###########################################################################
    def tearDown(self):
        self.link.delete()
        self.al.delete()
        self.kv1.delete()
        self.kv2.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_rvlist(self):
        response = self.client.get('/hostinfo/host_summary/hosths')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostpage.template', 'host/base.html']
            )
        self.assertEquals(response.context['host'], 'hosths')
        self.assertEquals(response.context['hostlink'], ['(<a class="foreignlink" href="http://code.google.com/p/hostinfo">hslink</a>)'])
        self.assertEquals(response.context['kvlist'], [('hskey', [self.kv1, self.kv2])])
        self.assertEquals(response.context['aliases'], ['a1'])

    ###########################################################################
    def test_rvlist_wiki(self):
        response = self.client.get('/hostinfo/host_summary/hosths/wiki')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals([t.name for t in response.templates], ['hostpage.wiki'])
        self.assertEquals(response.context['host'], 'hosths')
        self.assertEquals(response.context['hostlink'], ['[http://code.google.com/p/hostinfo hslink]'])
        self.assertEquals(response.context['kvlist'], [('hskey', [self.kv1, self.kv2])])
        self.assertEquals(response.context['aliases'], ['a1'])


###############################################################################
class test_url_host_edit(TestCase):
    ###########################################################################
    def setUp(self):
        self.user = User.objects.create_user('fred', 'fred@example.com', 'secret')
        self.user.save()
        self.client = Client()
        self.client.login(username='fred', password='secret')
        self.host = Host(hostname='hosteh')
        self.host.save()
        self.key1 = AllowedKey(key='ehkey1', validtype=2)
        self.key1.save()
        self.key2 = AllowedKey(key='ehkey2', validtype=1)
        self.key2.save()
        self.kv1 = KeyValue(hostid=self.host, keyid=self.key1, value='oldval')
        self.kv1.save()
        self.key3 = AllowedKey(key='ehkey3', validtype=1, restrictedFlag=True)
        self.key3.save()
        self.rv1 = RestrictedValue(keyid=self.key3, value='true')
        self.rv1.save()
        self.rv2 = RestrictedValue(keyid=self.key3, value='false')
        self.rv2.save()
        self.kv2 = KeyValue(hostid=self.host, keyid=self.key3, value='false')
        self.kv2.save()

    ###########################################################################
    def tearDown(self):
        self.kv1.delete()
        self.kv2.delete()
        self.rv1.delete()
        self.rv2.delete()
        self.host.delete()
        self.key1.delete()
        self.key2.delete()
        self.key3.delete()
        self.user.delete()

    ###########################################################################
    def test_hostselect(self):
        response = self.client.get('/hostinfo/hostedit/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostedit.template', 'host/base.html']
            )

    ###########################################################################
    def test_hostpicked(self):
        response = self.client.post('/hostinfo/hostedit/hosteh/', {'hostname': 'hosteh'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostedit.template', 'host/base.html', 'host/hostediting.template']
            )
        self.assertEquals(response.context['host'], 'hosteh')
        self.assertEquals(response.context['editing'], True)
        self.assertEquals(
            response.context['kvlist'],
            [('ehkey1', [self.kv1], 'list', []), (u'ehkey3', [self.kv2], u'single', ['-Unknown-', u'false', u'true'])]
            )
        self.assertEquals(response.context['keylist'], [self.key2])

    ###########################################################################
    def test_hostedited(self):
        response = self.client.post(
            '/hostinfo/hostedit/hosteh/',
            {'hostname': 'hosteh', '_hostediting': 'hosteh', 'ehkey1.0': 'newval', '_newkey.new': 'ehkey3', '_newvalue.new': 'v2'},
            follow=True
            )
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostedit.template', 'host/base.html', 'host/hostediting.template']
            )
        # kv=KeyValue.objects.filter(hostid=self.host, keyid=self.key1)
        # self.assertEquals(kv[0].value, 'newval')
        # kv=KeyValue.objects.filter(hostid=self.host, keyid=self.key3)
        # self.assertEquals(kv[0].value, 'v2')
        # TODO


###############################################################################
class test_url_hostlist(TestCase):
    """
    (r'^hostlist/(?P<criteria>.*)/(?P<options>opts=.*)?$', 'doHostlist'),
    (r'^host/$', 'doHostlist'),
    """
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.host1 = Host(hostname='hosthl1')
        self.host1.save()
        self.link = Links(hostid=self.host1, url='http://code.google.com/p/hostinfo', tag='hslink')
        self.link.save()
        self.host2 = Host(hostname='hosthl2')
        self.host2.save()
        self.alias = HostAlias(hostid=self.host2, alias='alias')
        self.alias.save()
        self.key = AllowedKey(key='urlkey')
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host2, keyid=self.key, value='val')
        self.kv1.save()
        getAkCache()

    ###########################################################################
    def tearDown(self):
        self.alias.delete()
        self.kv1.delete()
        self.key.delete()
        self.link.delete()
        self.host1.delete()
        self.host2.delete()

    ###########################################################################
    def test_hostlist(self):
        """ Test that no criteria gets nowhere """
        response = self.client.get('/hostinfo/hostlist/')
        self.assertEquals(response.status_code, 404)

    ###########################################################################
    def test_badkey(self):
        response = self.client.get('/hostinfo/hostlist/badkey=foo/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            sorted([t.name for t in response.templates]),
            ['host/base.html', 'host/hostlist.template']
            )
        self.assertEquals(response.context['error'].msg, 'Must use an existing key, not badkey')

    ###########################################################################
    def test_withcriteria(self):
        response = self.client.get('/hostinfo/hostlist/urlkey=foo/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            sorted([t.name for t in response.templates]),
            ['host/base.html', 'host/hostlist.template']
            )

    ###########################################################################
    def test_withoptions(self):
        response = self.client.get('/hostinfo/hostlist/urlkey=foo/dates')
        self.assertEquals(response.status_code, 301)
        response = self.client.get('/hostinfo/hostlist/urlkey=foo/dates', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            sorted([t.name for t in response.templates]),
            ['host/base.html', 'host/hostlist.template']
            )

    ###########################################################################
    def test_nohosts(self):
        response = self.client.get('/hostinfo/host/')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['count'], 2)
        self.assertEquals(
            response.context['hostlist'],
            [
                (u'hosthl1', [], ['<a class="foreignlink" href="http://code.google.com/p/hostinfo">hslink</a>']),
                (u'hosthl2', [(u'urlkey', [self.kv1])], [])
            ]
            )

    ###########################################################################
    def test_hostcriteria(self):
        response = self.client.get('/hostinfo/hostlist/hosthl2/')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['count'], 1)
        self.assertEquals(response.context['csvavailable'], '/hostinfo/csv/hosthl2')
        self.assertEquals(response.context['hostlist'], [(u'hosthl2', [(u'urlkey', [self.kv1])], [])])

    ###########################################################################
    def test_multihostcriteria(self):
        response = self.client.get('/hostinfo/hostlist/urlkey.eq.val/')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        kv = KeyValue.objects.filter(hostid=self.host2, keyid=self.key)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['title'], 'urlkey.eq.val')
        self.assertEquals(response.context['count'], 1)
        self.assertEquals(response.context['hostlist'], [(u'hosthl2', [(u'urlkey', [self.kv1])], [])])

    ###########################################################################
    def test_host_origin_option(self):
        response = self.client.get('/hostinfo/hostlist/urlkey.ne.bar/opts=origin')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['count'], 2)
        self.assertEquals(response.context['origin'], True)
        self.assertEquals(
            response.context['hostlist'],
            [
                (self.host1.hostname, [], ['<a class="foreignlink" href="http://code.google.com/p/hostinfo">hslink</a>']),
                (self.host2.hostname, [(self.key.key, [self.kv1])], [])
            ]
            )

    ###########################################################################
    def test_host_both_option(self):
        response = self.client.get('/hostinfo/hostlist/urlkey.ne.bar/opts=dates,origin')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['count'], 2)
        self.assertEquals(response.context['origin'], True)
        self.assertEquals(response.context['dates'], True)
        self.assertEquals(response.context['hostlist'], [
            (self.host1.hostname, [], ['<a class="foreignlink" href="http://code.google.com/p/hostinfo">hslink</a>']),
            (self.host2.hostname, [(self.key.key, [self.kv1])], [])
            ]
        )


###############################################################################
class test_url_csv(TestCase):
    """
    (r'^csv/$', 'doCsvreport'),
    (r'^csv/(?P<criteria>.*)/$', 'doCsvreport'),
    """
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.host1 = Host(hostname='hostcsv1')
        self.host1.save()
        self.host2 = Host(hostname='hostcsv2')
        self.host2.save()
        self.key = AllowedKey(key='csvkey')
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host2, keyid=self.key, value='val')
        self.kv1.save()
        getAkCache()

    ###########################################################################
    def tearDown(self):
        self.kv1.delete()
        self.key.delete()
        self.host1.delete()
        self.host2.delete()

    ###########################################################################
    def test_csv(self):
        response = self.client.get('/hostinfo/csv/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response["Content-Type"], "text/csv")
        self.assertEquals(response["Content-Disposition"], "attachment; filename=allhosts.csv")
        self.assertEquals(
            response.content,
            "hostname,csvkey\r\nhostcsv1,\r\nhostcsv2,val\r\n"
            )


###############################################################################
class test_url_hostwikitable(TestCase):
    """
    (r'^hostwikitable/(?P<criteria>.*?)(?P<options>/(?:order=|print=).*)?$', 'doHostwikiTable'),
    """
    ###########################################################################
    def setUp(self):
        self.client = Client()
        self.host1 = Host(hostname='hosthwt1')
        self.host1.save()
        self.link = Links(hostid=self.host1, url='http://code.google.com/p/hostinfo', tag='hslink')
        self.link.save()
        self.host2 = Host(hostname='hosthwt2')
        self.host2.save()
        self.alias = HostAlias(hostid=self.host2, alias='alias')
        self.alias.save()
        self.key = AllowedKey(key='hwtkey')
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host2, keyid=self.key, value='val')
        self.kv1.save()
        getAkCache()

    ###########################################################################
    def tearDown(self):
        self.alias.delete()
        self.kv1.delete()
        self.key.delete()
        self.link.delete()
        self.host1.delete()
        self.host2.delete()

    ###########################################################################
    def test_wikitable(self):
        response = self.client.get('/hostinfo/hostwikitable/hwtkey.ne.val')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEquals(response.content, "{| border=1\n|-\n!Hostname\n|-\n| [[Host:hosthwt1|hosthwt1]]\n|}\n")

    ###########################################################################
    def test_wikitable_print(self):
        response = self.client.get('/hostinfo/hostwikitable/hwtkey.def/print=hwtkey/order=hwtkey')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEquals(response.content, "{| border=1\n|-\n!Hostname\n!Hwtkey\n|-\n| [[Host:hosthwt2|hosthwt2]]\n| val\n|}\n")


###############################################################################
class test_url_hostcmp(TestCase):
    """
    (r'^hostcmp/(?P<criteria>.*)/(?P<options>opts=.*)?$', 'doHostcmp'),
    """
    def setUp(self):
        self.client = Client()
        self.host1 = Host(hostname='hostuhc1')
        self.host1.save()
        self.host2 = Host(hostname='hostuhc2')
        self.host2.save()
        self.key = AllowedKey(key='uhckey')
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host1, keyid=self.key, value='val1')
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host2, keyid=self.key, value='val2')
        self.kv2.save()
        getAkCache()

    ###########################################################################
    def tearDown(self):
        self.kv1.delete()
        self.kv2.delete()
        self.key.delete()
        self.host1.delete()
        self.host2.delete()

    ###########################################################################
    def test_hostcmp(self):
        response = self.client.get('/hostinfo/hostcmp/uhckey.def/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('<title> Comparison of host details uhckey.def</title>', response.content)
        self.assertIn('<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>', response.content)
        self.assertIn('<a class="hostname" href="/hostinfo/host/hostuhc2">hostuhc2</a>', response.content)
        self.assertIn('<a class="keyname" href="/hostinfo/keylist/uhckey">uhckey</a>', response.content)
        self.assertIn('<a class="valuelink" href="/hostinfo/hostlist/uhckey.eq.val2">val2</a>', response.content)
        self.assertEquals(
            set([t.name for t in response.templates]),
            set(['host/multihost.template', 'host/base.html', 'host/showall.template'])
            )

    ###########################################################################
    def test_hostcmp_dates(self):
        response = self.client.get('/hostinfo/hostcmp/uhckey.def/opts=dates')
        self.assertEquals(response.status_code, 200)
        self.assertIn('<title> Comparison of host details uhckey.def</title>', response.content)
        self.assertIn('<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>', response.content)
        self.assertIn('<input type=checkbox name=options value=dates  checked  >Show Dates<br>', response.content)
        self.assertIn('<input type=checkbox name=options value=origin  >Show Origin<br>', response.content)
        self.assertIn('Modified:', response.content)
        self.assertIn('Created:', response.content)
        self.assertEquals(
            set([t.name for t in response.templates]),
            set(['host/multihost.template', 'host/base.html', 'host/showall.template'])
            )

    ###########################################################################
    def test_hostcmp_origin(self):
        response = self.client.get('/hostinfo/hostcmp/uhckey.def/opts=origin')
        self.assertEquals(response.status_code, 200)
        self.assertIn('<title> Comparison of host details uhckey.def</title>', response.content)
        self.assertIn('<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>', response.content)
        self.assertIn('<input type=checkbox name=options value=origin  checked  >Show Origin<br>', response.content)
        self.assertIn('<input type=checkbox name=options value=dates  >Show Dates<br>', response.content)
        self.assertIn('Origin:', response.content)
        self.assertEquals(
            set([t.name for t in response.templates]),
            set(['host/multihost.template', 'host/base.html', 'host/showall.template'])
            )


###############################################################################
class test_orderhostlist(TestCase):
    def setUp(self):
        self.key1 = AllowedKey(key='ohlkey1')
        self.key1.save()
        self.key2 = AllowedKey(key='ohlkey2', validtype=2)
        self.key2.save()
        self.hosts = []
        self.kvals = []
        for h in ('a', 'b', 'c', 'd', 'e'):
            t = Host(hostname=h)
            t.save()
            self.hosts.append(t)
            kv = KeyValue(hostid=t, keyid=self.key1, value=h)
            kv.save()
            self.kvals.append(kv)
            kv = KeyValue(hostid=t, keyid=self.key2, value='%s1' % h)
            kv.save()
            self.kvals.append(kv)
            kv = KeyValue(hostid=t, keyid=self.key2, value='2')
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

    ###########################################################################
    def test_order(self):
        out = orderHostList(self.hosts, 'ohlkey1')
        self.hosts.sort(key=lambda x: x.hostname)
        self.assertEquals(out, self.hosts)

    ###########################################################################
    def test_reverse(self):
        out = orderHostList(self.hosts, '-ohlkey1')
        self.hosts.sort(key=lambda x: x.hostname, reverse=True)
        self.assertEquals(out, self.hosts)

    ###########################################################################
    def test_noval(self):
        """ Output will be in hash order as all will sort equally
        """
        out = orderHostList(self.hosts, 'badkey')
        self.assertEquals(len(out), len(self.hosts))

    ###########################################################################
    def test_list(self):
        out = orderHostList(self.hosts, 'ohlkey2')
        self.assertEquals(out, self.hosts)

# EOF
