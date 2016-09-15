# Test rig for hostinfo

# Written by Dougal Scott <dougal.scott@gmail.com>

#    Copyright (C) 2016 Dougal Scott
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
import json
import os
import sys
import tempfile
import time

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .models import HostinfoException, ReadonlyValueException, RestrictedValueException
from .models import Host, HostAlias, AllowedKey, KeyValue, RestrictedValue, Links

from .models import validateDate, clearAKcache, calcKeylistVals
from .models import parseQualifiers, getMatches
from .models import getHost, checkHost, getAK
from .models import addKeytoHost, run_from_cmdline

from .views import hostviewrepr, hostData
from .views import orderHostList
from .edits import getHostMergeKeyData


###############################################################################
class test_SingleKey(TestCase):
    """ Test operations on a single values key """
    def setUp(self):
        clearAKcache()
        self.host = Host(hostname='host')
        self.host.save()
        self.key = AllowedKey(key='single', validtype=1)
        self.key.save()
        self.num = AllowedKey(key='number', validtype=1, numericFlag=True)
        self.num.save()

    ###########################################################################
    def tearDown(self):
        self.num.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def checkValue(self, host, key):
        keyid = getAK(key)
        hostid = getHost(host)
        kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
        return kv[0].value

    ###########################################################################
    def checkNumValue(self, host, key):
        keyid = getAK(key)
        hostid = getHost(host)
        kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
        return kv[0].numvalue

    ###########################################################################
    def test_numeric_nonnumeric(self):
        """Test numeric keys with a non-numeric value """
        addKeytoHost(host='host', key='number', value='a')
        self.assertEquals(self.checkValue('host', 'number'), 'a')
        self.assertIsNone(self.checkNumValue('host', 'number'))

    ###########################################################################
    def test_numeric_numeric(self):
        """Test numeric keys with a numeric value """
        addKeytoHost(host='host', key='number', value='100')
        self.assertEquals(self.checkValue('host', 'number'), '100')
        self.assertEquals(self.checkNumValue('host', 'number'), 100)

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
        clearAKcache()
        self.host = Host(hostname='host')
        self.host.save()
        self.key = AllowedKey(key='lk_list', validtype=2)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def checkValue(self, host, key):
        keyid = getAK(key)
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
        addKeytoHost(host='host', key='lk_list', value='a')
        self.assertEquals(self.checkValue('host', 'lk_list'), 'a')

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
        addKeytoHost(host='host', key='lk_list', value='a')
        addKeytoHost(host='host', key='lk_list', value='a')
        self.assertEquals(self.checkValue('host', 'lk_list'), 'a')

    ###########################################################################
    def test_changevalue(self):
        """ Add a value without override"""
        addKeytoHost(host='host', key='lk_list', value='a')
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='host', key='lk_list', value='b')
        self.assertEquals(self.checkValue('host', 'lk_list'), 'a')

    ###########################################################################
    def test_override(self):
        """ Add a value with override"""
        addKeytoHost(host='host', key='lk_list', value='a')
        addKeytoHost(host='host', key='lk_list', value='b', updateFlag=True)
        self.assertEquals(self.checkValue('host', 'lk_list'), 'b')

    ###########################################################################
    def test_nohost(self):
        """ Test adding to a host that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host='hostnot', key='lk_list', value='b')

    ###########################################################################
    def test_append(self):
        """ Test to make sure we can append
        """
        addKeytoHost(host='host', key='lk_list', value='a')
        addKeytoHost(host='host', key='lk_list', value='b', appendFlag=True)
        self.assertEquals(self.checkValue('host', 'lk_list'), ['a', 'b'])

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
        clearAKcache()
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
        clearAKcache()
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
        keyid = getAK(key)
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
        clearAKcache()
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
        clearAKcache()
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
        clearAKcache()
        self.key = AllowedKey(key='kpq', validtype=1)
        self.key.save()

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
        self.assertEquals(parseQualifiers(['kpq.leneq.1']), [('leneq', 'kpq', '1')])
        self.assertEquals(parseQualifiers(['kpq.lenlt.2']), [('lenlt', 'kpq', '2')])
        self.assertEquals(parseQualifiers(['kpq.lengt.3']), [('lengt', 'kpq', '3')])
        self.assertEquals(parseQualifiers(['HOST.hostre']), [('hostre', 'host', '')])
        self.assertEquals(parseQualifiers(['HOST']), [('host', None, 'host')])
        self.assertEquals(parseQualifiers([]), [])

    ###########################################################################
    def test_hostmatch(self):
        host = Host(hostname='hosta.lt.example.com')
        host.save()
        self.assertEquals(parseQualifiers(['hosta.lt.example.com']), [('host', None, 'hosta.lt.example.com')])
        host.delete()
        with self.assertRaises(HostinfoException):
            parseQualifiers(['hostb.lt.example.com'])

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
        clearAKcache()
        # hostA: single=100, list==[alpha, beta], date=2012/12/25
        # hostB: list=[alpha]
        self.host = Host(hostname='hostgma')
        self.host.save()

        self.host2 = Host(hostname='hostgmb')
        self.host2.save()

        self.singlekey = AllowedKey(key='single', validtype=1)
        self.singlekey.save()
        addKeytoHost(host='hostgma', key='single', value='100')

        self.numberkey = AllowedKey(key='number', validtype=1, numericFlag=True)
        self.numberkey.save()
        addKeytoHost(host='hostgma', key='number', value='100')
        addKeytoHost(host='hostgmb', key='number', value='2')

        self.listkey = AllowedKey(key='list', validtype=2)
        self.listkey.save()
        addKeytoHost(host='hostgma', key='list', value='alpha')
        addKeytoHost(host='hostgma', key='list', value='beta', appendFlag=True)
        addKeytoHost(host='hostgmb', key='list', value='alpha')

        self.datekey = AllowedKey(key='date', validtype=3)
        self.datekey.save()
        addKeytoHost(host='hostgma', key='date', value='2012/12/25')

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
        self.assertEquals(
            getMatches([('leneq', 'list', '2')]),
            [self.host.id]
            )

    ###########################################################################
    def test_lengt(self):
        self.assertEquals(
            getMatches([('lengt', 'list', '3')]),
            []
            )

    ###########################################################################
    def test_lenlt(self):
        # Why people, why?!
        if sys.version_info.major == 2:
            tester = self.assertItemsEqual
        else:
            tester = self.assertCountEqual
        tester(
            getMatches([('lenlt', 'list', '2')]),
            [self.host.id, self.host2.id]
            )

    ###########################################################################
    def test_badlenlt(self):
        with self.assertRaises(HostinfoException) as cm:
            getMatches([('lenlt', 'list', 'foo')])
        self.assertEquals(cm.exception.msg, "Length must be an integer, not foo")

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
        self.assertEquals(
            getMatches([('equal', 'number', '2.0')]),
            [self.host2.id]
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
        self.assertEquals(
            set(getMatches([('unequal', 'number', '100.0')])),
            set([self.host2.id])
            )

    ###########################################################################
    def test_greaterthan(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25, number=100
        # hostB: list=[alpha], number=2
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
        self.assertEquals(
            getMatches([('greaterthan', 'number', '10')]),
            [self.host.id]
            )

    ###########################################################################
    def test_lessthan(self):
        # hostA: single=100, list==[alpha, beta], date=2012/12/25, number=100
        # hostB: list=[alpha], number=2
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
        self.assertEquals(
            getMatches([('lessthan', 'number', '90')]),
            [self.host2.id]
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
        clearAKcache()
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
class test_getAK(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.ak = AllowedKey(key='ak_checkkey')
        self.ak.save()

    ###########################################################################
    def tearDown(self):
        self.ak.delete()

    ###########################################################################
    def test_checkexists(self):
        rc = getAK('ak_checkkey')
        self.assertTrue(rc)

    ###########################################################################
    def test_checknoexists(self):
        with self.assertRaises(HostinfoException) as cm:
            getAK('ak_badkey')
        self.assertEquals(cm.exception.msg, "Must use an existing key, not ak_badkey")


###############################################################################
class test_checkHost(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
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
class test_cmd_hostinfo_xml(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.h1 = Host(hostname='xh1', origin='me')
        self.h1.save()
        self.h2 = Host(hostname='xh2', origin='you')
        self.h2.save()
        self.ak1 = AllowedKey(key='xak1', numericFlag=True, desc="Test Key")
        self.ak1.save()
        self.ak2 = AllowedKey(key='xak2', restrictedFlag=True, desc="Restricted Test")
        self.ak2.save()
        self.rv = RestrictedValue(keyid=self.ak2, value='xkv3')
        self.rv.save()
        self.kv1 = KeyValue(hostid=self.h1, keyid=self.ak1, value='1', origin='foo')
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.h2, keyid=self.ak1, value='xkv2', origin='bar')
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.h1, keyid=self.ak2, value='xkv3', origin='baz')
        self.kv3.save()
        self.alias = HostAlias(hostid=self.h1, alias='xhalias')
        self.alias.save()

    ###########################################################################
    def tearDown(self):
        self.rv.delete()
        self.alias.delete()
        self.kv1.delete()
        self.kv2.delete()
        self.kv3.delete()
        self.h1.delete()
        self.h2.delete()
        self.ak1.delete()
        self.ak2.delete()

    ###########################################################################
    def test_xml_numerickey(self):
        namespace = self.parser.parse_args(['--xml', '-p', 'xak1'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn('<name>xak1</name>', output[0])
        self.assertIn('<desc>Test Key</desc>', output[0])
        self.assertIn('<numericFlag>True</numericFlag>', output[0])
        self.assertIn('<auditFlag>True</auditFlag>', output[0])
        self.assertIn('<type>single</type>', output[0])
        self.assertIn('<confitem key="xak1">1</confitem>', output[0])

    ###########################################################################
    def test_xml_restrictedkey(self):
        namespace = self.parser.parse_args(['--xml', '-p', 'xak2'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn('<name>xak2</name>', output[0])
        self.assertIn('<desc>Restricted Test</desc>', output[0])
        self.assertIn('<numericFlag>False</numericFlag>', output[0])
        self.assertIn('<auditFlag>True</auditFlag>', output[0])
        self.assertIn('<restricted>', output[0])
        self.assertIn('<value>xkv3</value>', output[0])
        self.assertIn('<confitem key="xak2">xkv3</confitem>', output[0])

    ###########################################################################
    def test_hostinfo_xml(self):
        """ Test outputting hosts only in xml mode """
        namespace = self.parser.parse_args(['--xml'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn('<hostname>xh1</hostname>', output[0])
        self.assertIn('<hostname>xh2</hostname>', output[0])
        self.assertNotIn('confitem', output[0])
        # TODO: Replace with something that pulls the whole xml apart


###############################################################################
class test_cmd_hostinfo(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo import Command
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
        hname = 'good.lt.bad'
        th1 = Host(hostname=hname, origin='me')
        th1.save()
        namespace = self.parser.parse_args(['--host', hname])
        output = self.cmd.handle(namespace)
        self.assertIn(hname, output[0])
        self.assertEquals(output[1], 0)
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
        self.assertEquals(cm.exception.msg, "Must use an existing key, not badkey")

    ###########################################################################
    def test_hostinfo_json(self):
        namespace = self.parser.parse_args(['--json'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        data = json.loads(output[0])
        self.assertTrue('h1' in data)
        self.assertTrue('h2' in data)

    ###########################################################################
    def test_hostinfo_jsonp(self):
        namespace = self.parser.parse_args(['--json', '-p', 'ak1', '-p', 'ak2'])
        output = self.cmd.handle(namespace)
        data = json.loads(output[0])
        self.assertEquals(data['h2'], {u'ak1': [u'kv2']})

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
    def test_hostinfo_count(self):
        namespace = self.parser.parse_args(['--count'])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('2', 0))

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

    ###########################################################################
    def test_hostinfo_valuereport_badkey(self):
        """ Make sure the key exists for a valuereport - Iss06 """
        namespace = self.parser.parse_args(['--valuereport', 'badkey'])
        with self.assertRaises(HostinfoException):
            self.cmd.handle(namespace)


###############################################################################
class test_cmd_addalias(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_addalias import Command
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
    def test_alias_of_alias(self):
        """ Can we create an alias to an alias
        """
        host = Host(hostname='aoahost')
        host.save()
        alias = HostAlias(hostid=host, alias='oldalias')
        alias.save()
        namespace = self.parser.parse_args(['oldalias', 'newalias'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        newalias = HostAlias.objects.get(alias='newalias')
        self.assertEquals(newalias.hostid, host)
        newaliases = HostAlias.objects.filter(hostid=host)
        self.assertEquals(len(newaliases), 2)
        for a in newaliases:
            a.delete()
        host.delete()

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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_addhost import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_addkey import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_addrestrictedvalue import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_addvalue import Command
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
    def test_whitespacevalue(self):
        """ Confirm that values are stripped before adding - Iss02 """
        key = AllowedKey(key='key_addvalue_t1', validtype=1)
        key.save()
        namespace = self.parser.parse_args(['key_addvalue_t1= VALUE', 'testhost'])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        kv = KeyValue.objects.filter()[0]
        self.assertEquals(kv.hostid, self.host)
        self.assertEquals(kv.value, 'value')
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_deletealias import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_deletehost import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_deleterestrictedvalue import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_deletevalue import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_history import Command

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
        host = Host(hostname='host_history_o')
        host.save()
        ak = AllowedKey(key='key4_dv')
        ak.save()
        kv = KeyValue(keyid=ak, hostid=host, value='historic', origin='kv_origin')
        kv.save()
        namespace = self.parser.parse_args(['-o', 'host_history_o'])
        output = self.cmd.handle(namespace)
        self.assertTrue('kv_origin' in output[0])
        self.assertTrue(self.t in output[0])
        kv.delete()
        ak.delete()
        host.delete()

    ###########################################################################
    def test_actor(self):
        """ Make sure that we are saving the actor properly
        """
        # Currently actor is not supported
        return
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
        self.assertTrue('Host:host_history_ha added' in output[0])
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
        self.assertTrue('added host_history_va:key3_dv=historic' in output[0])
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
        self.assertTrue('deleted host_history_vd:key4_dv=historic' in output[0])
        self.assertTrue(self.t in output[0])
        ak.delete()
        host.delete()

    ###########################################################################
    def test_noaudit(self):
        return  # TODO - fix this
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_import import Command
        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.stderr = sys.stderr
        sys.stderr = StringIO()

    ###########################################################################
    def tearDown(self):
        sys.stderr = self.stderr

    ###########################################################################
    def test_badfile(self):
        namespace = self.parser.parse_args(['badfile'])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "File badfile doesn't exist")

    ###########################################################################
    def test_basic_import(self):
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(b"""
        <hostinfo> <key> <name>importkey</name> <type>single</type>
        <readonlyFlag>False</readonlyFlag> <auditFlag>False</auditFlag>
        <docpage>None</docpage> <desc>Testing import key</desc> </key>
        <host docpage="None" > <hostname>importhost</hostname>
        <data> <confitem key="importkey">4</confitem> </data> </host> </hostinfo>""")
        tmpf.close()
        namespace = self.parser.parse_args([tmpf.name])
        self.cmd.handle(namespace)
        try:
            os.unlink(tmpf.name)
        except OSError:
            pass
        host = Host.objects.get(hostname='importhost')
        key = AllowedKey.objects.get(key='importkey')
        self.assertEquals(key.desc, 'Testing import key')
        self.assertEquals(key.readonlyFlag, False)
        self.assertEquals(key.auditFlag, False)
        keyval = KeyValue.objects.get(hostid=host, keyid=key)
        self.assertEquals(keyval.value, '4')

    ###########################################################################
    def test_list_import(self):
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(b"""<hostinfo> <key> <name>importlistkey</name> <type>list</type>
        <readonlyFlag>True</readonlyFlag> <auditFlag>True</auditFlag>
        <docpage>None</docpage> <desc>Listkey</desc> </key> <host docpage="None" >
        <hostname>importhost2</hostname> <data>
        <confitem key="importlistkey">foo</confitem>
        <confitem key="importlistkey">bar</confitem> </data> </host> </hostinfo>""")
        tmpf.close()
        namespace = self.parser.parse_args([tmpf.name])
        self.cmd.handle(namespace)
        try:
            os.unlink(tmpf.name)
        except OSError:
            pass
        host = Host.objects.get(hostname='importhost2')
        key = AllowedKey.objects.get(key='importlistkey')
        self.assertEquals(key.readonlyFlag, True)
        self.assertEquals(key.auditFlag, True)
        keyvals = KeyValue.objects.filter(hostid=host, keyid=key)
        self.assertEquals(len(keyvals), 2)
        vals = sorted([kv.value for kv in keyvals])
        self.assertEquals(['bar', 'foo'], vals)

    ###########################################################################
    def test_restricted_import(self):
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(b"""<hostinfo><key><name>importrestkey</name>
        <type>single</type> <readonlyFlag>False</readonlyFlag>
        <auditFlag>True</auditFlag> <docpage></docpage> <desc>Operating System</desc>
        <restricted> <value>alpha</value> <value>beta</value> </restricted> </key>
        <host docpage="None" > <hostname>importhost3</hostname> <data>
        <confitem key="importrestkey">alpha</confitem> </data> </host> </hostinfo>""")
        tmpf.close()
        namespace = self.parser.parse_args([tmpf.name])
        self.cmd.handle(namespace)
        try:
            os.unlink(tmpf.name)
        except OSError:
            pass
        host = Host.objects.get(hostname='importhost3')
        key = AllowedKey.objects.get(key='importrestkey')
        self.assertEquals(key.readonlyFlag, False)
        self.assertEquals(key.auditFlag, True)
        keyvals = KeyValue.objects.get(hostid=host, keyid=key)
        self.assertEquals(keyvals.value, 'alpha')

    ###########################################################################
    def test_change_existingkey(self):
        # TODO
        pass

    ###########################################################################
    def test_verbose(self):
        # TODO
        pass

    ###########################################################################
    def test_kidding(self):
        # TODO
        pass


###############################################################################
class test_cmd_listalias(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_listalias import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_listrestrictedvalue import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_mergehost import Command
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
        sys.stderr = StringIO()

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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_renamehost import Command
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
        hosts = Host.objects.filter(hostname='renhost')
        self.assertEquals(len(hosts), 0)

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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_replacevalue import Command
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
        sys.stderr = StringIO()

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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_showkey import Command
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
        clearAKcache()
        import argparse
        from .commands.cmd_hostinfo_undolog import Command
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
        clearAKcache()
        self.oldargv = sys.argv
        self.stderr = sys.stderr
        sys.stderr = StringIO()

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
        clearAKcache()
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
            {'srchost': 'merge1', 'dsthost': 'merge2', '_hostmerging': True},
            follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('host/hostmerge.template')
        self.assertTemplateUsed('host/base.template')
        self.assertTemplateUsed('host/hostmergeing.template')
        # TODO
        # host = Host.objects.filter(hostname='merge1')
        # self.assertEquals(len(host), 0)
        # host = Host.objects.filter(hostname='merge2')
        # self.assertEquals(len(host), 1)
        # kv = KeyValue.objects.filter(hostid=self.host2, keyid=self.key)
        # self.assertEquals(kv[0].value, 'foo')


###############################################################################
class test_url_hostrename(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
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

        self.assertIn(b'urenamehost1 has been successfully renamed to urenamed', response.content)

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
        clearAKcache()
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
        clearAKcache()
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
        clearAKcache()
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
        self.assertEquals(response.context['total'], 2)      # Number of hosts
        self.assertEquals(response.context['numvals'], 1)    # Number of different values
        self.assertEquals(response.context['pctundef'], 50)  # % hosts with key not def
        self.assertEquals(response.context['numundef'], 1)   # Num hosts with key not def
        self.assertEquals(response.context['pctdef'], 50)    # % hosts with key defined
        self.assertEquals(response.context['numdef'], 1)     # Num hosts with key defined
        self.assertEquals(response.context['vallist'], [('foo', 1, 100)])    # Key, Value, Percentage

    ###########################################################################
    def test_badkey(self):
        response = self.client.get('/hostinfo/keylist/badkey/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' in response.context)
        self.assertEquals(
            sorted([t.name for t in response.templates]),
            ['host/base.html', 'host/keylist.template']
            )


###############################################################################
class test_hostviewrepr(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.key1 = AllowedKey(key='hvrkey1', validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key='hvrkey2', validtype=1)
        self.key2.save()
        self.host = Host(hostname='hvrhost1')
        self.host.save()
        self.host2 = Host(hostname='hvrhost2')
        self.host2.save()
        self.kv1 = KeyValue(hostid=self.host, keyid=self.key1, value='foo')
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host, keyid=self.key2, value='bar')
        self.kv2.save()

    ###########################################################################
    def tearDown(self):
        self.kv1.delete()
        self.key1.delete()
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_view(self):
        """ Test a simple hostview repr """
        ans = hostviewrepr('hvrhost1')
        self.assertEquals(ans, [
            (u'hvrkey1', [self.kv1]),
            (u'hvrkey2', [self.kv2])
            ]
            )

    ###########################################################################
    def test_empty(self):
        """ Test a hostview of an empty host """
        ans = hostviewrepr('hvrhost2')
        self.assertEquals(ans, [])

    ###########################################################################
    def test_printers(self):
        """ Test a hostview specifying what to print """
        ans = hostviewrepr('hvrhost1', printers=['hvrkey1'])
        self.assertEquals(ans, [(u'hvrkey1', [self.kv1])])

    ###########################################################################
    def test_printer_with_missing(self):
        """ hostviewrepr printing a host without that print value"""
        kv = KeyValue(hostid=self.host2, keyid=self.key1, value='baz')
        kv.save()
        ans = hostviewrepr('hvrhost2', printers=['hvrkey2', 'hvrkey1'])
        self.assertEquals(ans, [
            (u'hvrkey2', []),
            (u'hvrkey1', [kv])
            ])
        kv.delete()


###############################################################################
class test_getHostMergeKeyData(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
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
        clearAKcache()
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
        response = self.client.get('/mediawiki/rvlist/rvlkey/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals([t.name for t in response.templates], ['mediawiki/restrval.wiki'])
        self.assertEquals(response.context['key'], 'rvlkey')
        self.assertEquals(len(response.context['rvlist']), 3)
        self.assertTrue(self.rv1 in response.context['rvlist'])
        self.assertTrue(self.rv2 in response.context['rvlist'])
        self.assertTrue(self.rv3 in response.context['rvlist'])


###############################################################################
class test_url_host_summary(TestCase):
    # (r'^host_summary/(?P<hostname>.*)$', 'doHostSummary'),
    ###########################################################################
    def setUp(self):
        clearAKcache()
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
        hostlist = response.context['hostlist'][0]
        self.assertEquals(hostlist['hostname'], 'hosths')
        self.assertEquals(hostlist['links'], ['<a class="foreignlink" href="http://code.google.com/p/hostinfo">hslink</a>'])
        self.assertEquals(hostlist['hostview'], [('hskey', [self.kv1, self.kv2])])
        self.assertEquals(hostlist['aliases'], ['a1'])

    ###########################################################################
    def test_rvlist_wiki(self):
        response = self.client.get('/mediawiki/host_summary/hosths')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals([t.name for t in response.templates], ['mediawiki/hostpage.wiki'])
        hostlist = response.context['hostlist'][0]
        self.assertEquals(hostlist['hostname'], 'hosths')
        self.assertEquals(hostlist['links'], ['[http://code.google.com/p/hostinfo hslink]'])
        self.assertEquals(hostlist['hostview'], [('hskey', [self.kv1, self.kv2])])
        self.assertEquals(hostlist['aliases'], ['a1'])


###############################################################################
class test_url_host_create(TestCase):
    ###########################################################################
    def setUp(self):
        self.user = User.objects.create_user('fred', 'fred@example.com', 'secret')
        self.user.save()
        self.client = Client()
        self.client.login(username='fred', password='secret')

    ###########################################################################
    def test_create_choose(self):
        response = self.client.get('/hostinfo/hostcreate/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('host/hostcreate.template')

    ###########################################################################
    def test_creation(self):
        response = self.client.post(
            '/hostinfo/hostcreate/darwin/',
            follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('host/hostcreate.template')
        self.assertTemplateUsed('host/base.template')
        host = Host.objects.filter(hostname='darwin')
        self.assertEquals(len(host), 1)


###############################################################################
class test_url_host_edit(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
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
        clearAKcache()
        self.client = Client()
        self.host1 = Host(hostname='a_hosthl1')
        self.host1.save()
        self.link = Links(hostid=self.host1, url='http://code.google.com/p/hostinfo', tag='hslink')
        self.link.save()
        self.host2 = Host(hostname='m_hosthl')
        self.host2.save()
        self.host3 = Host(hostname='z_hosthl2')
        self.host3.save()
        self.alias = HostAlias(hostid=self.host2, alias='alias')
        self.alias.save()
        self.key = AllowedKey(key='urlkey')
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host3, keyid=self.key, value='val')
        self.kv1.save()

    ###########################################################################
    def tearDown(self):
        self.alias.delete()
        self.kv1.delete()
        self.key.delete()
        self.link.delete()
        self.host1.delete()
        self.host2.delete()
        self.host3.delete()

    ###########################################################################
    def test_hostlist(self):
        """ Test that no criteria gets all hosts """
        response = self.client.get('/hostinfo/hostlist/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['count'], 3)
        self.assertEquals(response.context['hostlist'][0]['hostname'], 'a_hosthl1')
        self.assertEquals(response.context['hostlist'][1]['hostname'], 'm_hosthl')
        self.assertEquals(response.context['hostlist'][2]['hostname'], 'z_hosthl2')

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
        self.assertEquals(response.context['count'], 3)
        self.assertEquals(response.context['hostlist'][0]['hostname'], 'a_hosthl1')
        self.assertEquals(response.context['hostlist'][1]['hostname'], 'm_hosthl')
        self.assertEquals(response.context['hostlist'][2]['hostname'], 'z_hosthl2')

    ###########################################################################
    def test_hostcriteria(self):
        response = self.client.get('/hostinfo/hostlist/z_hosthl2/')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['count'], 1)
        self.assertEquals(response.context['csvavailable'], '/hostinfo/csv/z_hosthl2')
        self.assertEquals(response.context['hostlist'][0]['hostname'], 'z_hosthl2')

    ###########################################################################
    def test_multihostcriteria(self):
        response = self.client.get('/hostinfo/hostlist/urlkey.eq.val/')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        KeyValue.objects.filter(hostid=self.host2, keyid=self.key)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['title'], 'urlkey.eq.val')
        self.assertEquals(response.context['count'], 1)
        self.assertEquals(response.context['hostlist'][0]['hostname'], 'z_hosthl2')

    ###########################################################################
    def test_host_origin_option(self):
        response = self.client.get('/hostinfo/hostlist/urlkey.ne.bar/opts=origin')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['count'], 3)
        self.assertEquals(response.context['origin'], True)

    ###########################################################################
    def test_host_both_option(self):
        response = self.client.get('/hostinfo/hostlist/urlkey.ne.bar/opts=dates,origin')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('error' not in response.context)
        self.assertEquals(
            [t.name for t in response.templates],
            ['host/hostlist.template', 'host/base.html']
            )
        self.assertEquals(response.context['count'], 3)
        self.assertEquals(response.context['origin'], True)
        self.assertEquals(response.context['dates'], True)


###############################################################################
class test_url_csv(TestCase):
    """
    (r'^csv/$', 'doCsvreport'),
    (r'^csv/(?P<criteria>.*)/$', 'doCsvreport'),
    """
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.host1 = Host(hostname='hostcsv1')
        self.host1.save()
        self.host2 = Host(hostname='hostcsv2')
        self.host2.save()
        self.key = AllowedKey(key='csvkey')
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host2, keyid=self.key, value='val')
        self.kv1.save()

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
            b"hostname,csvkey\r\nhostcsv1,\r\nhostcsv2,val\r\n"
            )


###############################################################################
class test_url_hostwikitable(TestCase):
    """
    (r'^hostwikitable/(?P<criteria>.*?)(?P<options>/(?:order=|print=).*)?$', 'doHostwikiTable'),
    """
    ###########################################################################
    def setUp(self):
        clearAKcache()
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
        response = self.client.get('/mediawiki/hosttable/hwtkey.ne.val')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEquals(response.content, b"{| border=1\n|-\n!Hostname\n|-\n| [[Host:hosthwt1|hosthwt1]]\n|}\n")

    ###########################################################################
    def test_wikitable_print(self):
        response = self.client.get('/mediawiki/hosttable/hwtkey.def/print=hwtkey/order=hwtkey')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEquals(response.content, b"{| border=1\n|-\n!Hostname\n!Hwtkey\n|-\n| [[Host:hosthwt2|hosthwt2]]\n| val\n|}\n")


###############################################################################
class test_url_hostcmp(TestCase):
    """
    (r'^hostcmp/(?P<criteria>.*)/(?P<options>opts=.*)?$', 'doHostcmp'),
    """
    def setUp(self):
        clearAKcache()
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
        self.assertIn(b'<title> Comparison of host details uhckey.def</title>', response.content)
        self.assertIn(b'<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>', response.content)
        self.assertIn(b'<a class="hostname" href="/hostinfo/host/hostuhc2">hostuhc2</a>', response.content)
        self.assertIn(b'<a class="keyname" href="/hostinfo/keylist/uhckey">uhckey</a>', response.content)
        self.assertIn(b'<a class="valuelink" href="/hostinfo/hostlist/uhckey.eq.val2">val2</a>', response.content)
        self.assertEquals(
            set([t.name for t in response.templates]),
            set(['host/multihost.template', 'host/base.html', 'host/showall.template'])
            )

    ###########################################################################
    def test_hostcmp_dates(self):
        response = self.client.get('/hostinfo/hostcmp/uhckey.def/opts=dates')
        self.assertEquals(response.status_code, 200)
        self.assertIn(b'<title> Comparison of host details uhckey.def</title>', response.content)
        self.assertIn(b'<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>', response.content)
        self.assertIn(b'<input type=checkbox name=options value=dates  checked  >Show Dates', response.content)
        self.assertIn(b'<input type=checkbox name=options value=origin  >Show Origin', response.content)
        self.assertIn(b'Modified:', response.content)
        self.assertIn(b'Created:', response.content)
        self.assertEquals(
            set([t.name for t in response.templates]),
            set(['host/multihost.template', 'host/base.html', 'host/showall.template'])
            )

    ###########################################################################
    def test_hostcmp_origin(self):
        response = self.client.get('/hostinfo/hostcmp/uhckey.def/opts=origin')
        self.assertEquals(response.status_code, 200)
        self.assertIn(b'<title> Comparison of host details uhckey.def</title>', response.content)
        self.assertIn(b'<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>', response.content)
        self.assertIn(b'<input type=checkbox name=options value=origin  checked  >Show Origin', response.content)
        self.assertIn(b'<input type=checkbox name=options value=dates  >Show Dates', response.content)
        self.assertIn(b'Origin:', response.content)
        self.assertEquals(
            set([t.name for t in response.templates]),
            set(['host/multihost.template', 'host/base.html', 'host/showall.template'])
            )


###############################################################################
class test_orderhostlist(TestCase):
    def setUp(self):
        clearAKcache()
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


###############################################################################
class test_restHost_keylist(TestCase):
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.host = Host(hostname='hostrhkl')
        self.host.save()
        self.key = AllowedKey(key='rhkeykl', validtype=1, desc='testkey')
        self.key.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value='val')
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_keylist(self):
        response = self.client.get('/api/keylist/rhkeykl/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['key'], 'rhkeykl')
        self.assertEquals(ans['numdef'], 1)
        self.assertEquals(ans['numvals'], 1)
        self.assertEquals(ans['total'], 1)

    ###########################################################################
    def test_keylist_criteria(self):
        response = self.client.get('/api/keylist/rhkeykl/rhkeykl.defined/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['key'], 'rhkeykl')
        self.assertEquals(ans['numdef'], 1)
        self.assertEquals(ans['vallist'], [['val', 1, 100.0]])


###############################################################################
class test_restHost_query(TestCase):
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.host = Host(hostname='hostrhq')
        self.host.save()
        self.key = AllowedKey(key='rhqkey', validtype=1, desc='testkey')
        self.key.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value='val')
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_query(self):
        response = self.client.get('/api/query/rhqkey=val/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], '1 matching hosts')
        self.assertEquals(ans['hosts'][0]['hostname'], 'hostrhq')
        self.assertSequenceEqual(sorted(ans['hosts'][0].keys()), sorted(['id', 'hostname', 'url']))

    ###########################################################################
    def test_query_origin(self):
        response = self.client.get('/api/query/rhqkey=val/?origin=True')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertSequenceEqual(sorted(ans['hosts'][0].keys()), sorted(['id', 'hostname', 'url', 'origin']))

    ###########################################################################
    def test_query_multi(self):
        response = self.client.get('/api/query/rhqkey=val/?aliases=True&dates=True&links=True')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertSequenceEqual(sorted(ans['hosts'][0].keys()), sorted(['id', 'hostname', 'url', 'aliases', 'createdate', 'modifieddate', 'links']))

    ###########################################################################
    def test_query_keys(self):
        response = self.client.get('/api/query/rhqkey=val/?keys=rhqkey')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], '1 matching hosts')
        self.assertEquals(ans['hosts'][0]['hostname'], 'hostrhq')
        self.assertEquals(ans['hosts'][0]['keyvalues']['rhqkey'][0]['value'], 'val')

    ###########################################################################
    def test_query_multikeys(self):
        k2 = AllowedKey(key='rhqkey2', validtype=1, desc='testkey2')
        k2.save()
        kv2 = KeyValue(hostid=self.host, keyid=k2, value='val2')
        kv2.save()
        response = self.client.get('/api/query/rhqkey=val/?keys=rhqkey,rhqkey2')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], '1 matching hosts')
        self.assertEquals(ans['hosts'][0]['hostname'], 'hostrhq')
        self.assertEquals(ans['hosts'][0]['keyvalues']['rhqkey'][0]['value'], 'val')
        self.assertEquals(ans['hosts'][0]['keyvalues']['rhqkey2'][0]['value'], 'val2')
        kv2.delete()
        k2.delete()

    ###########################################################################
    def test_bad_query(self):
        response = self.client.get('/api/query/badkey=val/')
        self.assertEquals(response.status_code, 406)
        ans = json.loads(response.content.decode())
        self.assertIn('badkey', ans['error'])


###############################################################################
class test_restHost(TestCase):
    def setUp(self):
        self.client = Client()
        self.host = Host(hostname='hostrh')
        self.host.save()
        self.key = AllowedKey(key='rhkey', validtype=1, desc='testkey')
        self.key.save()
        self.listkey = AllowedKey(key='rhlist', validtype=2, desc='list key')
        self.listkey.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value='val')
        self.kv.save()
        self.alias1 = HostAlias(hostid=self.host, alias='rhalias')
        self.alias1.save()
        self.alias2 = HostAlias(hostid=self.host, alias='rhalias2')
        self.alias2.save()
        self.link = Links(hostid=self.host, url='http://localhost', tag='heur')
        self.link.save()

    ###########################################################################
    def tearDown(self):
        self.link.delete()
        self.alias1.delete()
        self.alias2.delete()
        self.kv.delete()
        self.key.delete()
        self.listkey.delete()
        self.host.delete()

    ###########################################################################
    def test_hostcreate(self):
        data = {"origin": "testorigin"}
        response = self.client.post('/api/host/noahsark', data=json.dumps(data), content_type='application/json')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['host']['hostname'], 'noahsark')
        host = Host.objects.get(hostname='noahsark')
        self.assertEqual(host.origin, 'testorigin')
        host.delete()

    ###########################################################################
    def test_hostlist(self):
        response = self.client.get('/api/host/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], '1 hosts')
        self.assertEquals(ans['hosts'][0]['hostname'], 'hostrh')

    ###########################################################################
    def test_host_byid(self):
        """ Getting a host by its id """
        response = self.client.get('/api/host/hostrh/')
        ans = json.loads(response.content.decode())
        hostid = ans['host']['id']
        response = self.client.get('/api/host/%d/' % hostid)
        ans = json.loads(response.content.decode())
        self.assertEquals(response.status_code, 200)
        self.assertEquals(ans['host']['hostname'], 'hostrh')

    ###########################################################################
    def test_hostdetails(self):
        response = self.client.get('/api/host/hostrh/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['host']['keyvalues']['rhkey'][0]['value'], 'val')

    ###########################################################################
    def test_alias_details(self):
        response = self.client.get('/api/host/rhalias/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['host']['keyvalues']['rhkey'][0]['value'], 'val')

    ###########################################################################
    def test_missing_details(self):
        response = self.client.get('/api/host/badhost/')
        self.assertEquals(response.status_code, 404)

    ###########################################################################
    def test_list_aliases(self):
        response = self.client.get('/api/alias/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['aliases'][0]['host']['hostname'], 'hostrh')
        self.assertIn(ans['aliases'][0]['alias'], ['rhalias', 'rhalias2'])

    ###########################################################################
    def test_list_hostalias(self):
        response = self.client.get('/api/host/hostrh/alias/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        al = [a['alias'] for a in ans['aliases']]
        self.assertEquals(sorted(al), ['rhalias', 'rhalias2'])

    ###########################################################################
    def test_get_alias(self):
        response = self.client.get('/api/host/hostrh/alias/rhalias/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['aliases'][0]['alias'], 'rhalias')

    ###########################################################################
    def test_set_alias(self):
        response = self.client.post('/api/host/hostrh/alias/rhalias3/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        aliases = HostAlias.objects.filter(hostid=self.host, alias='rhalias3')
        self.assertEqual(len(aliases), 1)

    ###########################################################################
    def test_set_duplicate_alias(self):
        response = self.client.post('/api/host/hostrh/alias/rhalias2/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'duplicate')
        aliases = HostAlias.objects.filter(hostid=self.host, alias='rhalias2')
        self.assertEqual(len(aliases), 1)

    ###########################################################################
    def test_delete_alias(self):
        response = self.client.delete('/api/host/hostrh/alias/rhalias2/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'deleted')
        aliases = HostAlias.objects.filter(hostid=self.host, alias='rhalias2')
        self.assertEqual(len(aliases), 0)

    ###########################################################################
    def test_list_keys(self):
        """ Test the listing of keys through the REST interface """
        response = self.client.get('/api/host/hostrh/key/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEqual(ans['keyvalues'][0]['value'], 'val')
        self.assertEqual(ans['keyvalues'][0]['key'], 'rhkey')

    ###########################################################################
    def test_get_keyval(self):
        """ Test the getting of keys through the REST interface """
        response = self.client.get('/api/host/hostrh/key/rhkey/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEqual(ans['keyvalues'][0]['value'], 'val')
        self.assertEqual(ans['keyvalues'][0]['key'], 'rhkey')

    ###########################################################################
    def test_set_keyval(self):
        """ Test the setting of keys through the REST interface """
        response = self.client.post('/api/host/hostrh/key/rhkey/baz')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'updated')
        self.assertEqual(ans['keyvalues'][0]['value'], 'baz')
        self.assertEqual(ans['keyvalues'][0]['key'], 'rhkey')

    ###########################################################################
    def test_delete_keyval(self):
        response = self.client.delete('/api/host/hostrh/key/rhkey/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'deleted')
        kvs = KeyValue.objects.filter(hostid=self.host, keyid=self.key)
        self.assertEqual(len(kvs), 0)

    ###########################################################################
    def test_delete_from_list(self):
        """ Delete values from a list through REST """
        lkey = AllowedKey(key='rhlist2', validtype=2, desc='list key for deleting')
        lkey.save()
        addKeytoHost(host='hostrh', key='rhlist2', value='a')
        addKeytoHost(host='hostrh', key='rhlist2', value='b', appendFlag=True)
        addKeytoHost(host='hostrh', key='rhlist2', value='c', appendFlag=True)
        response = self.client.delete('/api/host/hostrh/key/rhlist2/b')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'deleted')
        kvs = KeyValue.objects.filter(hostid=self.host, keyid=lkey)
        self.assertEqual(len(kvs), 2)
        lkey.delete()

    ###########################################################################
    def test_append_keyval(self):
        """ Append values to a list through REST """
        response = self.client.post('/api/host/hostrh/key/rhlist/alpha')
        response = self.client.post('/api/host/hostrh/key/rhlist/beta')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'appended')
        kvs = KeyValue.objects.filter(hostid=self.host, keyid=self.listkey)
        self.assertEqual(len(kvs), 2)

    ###########################################################################
    def test_create_keyval(self):
        tmpkey = AllowedKey(key='tmprhkey', validtype=1)
        tmpkey.save()
        response = self.client.post('/api/host/hostrh/key/tmprhkey/noob')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'created')
        kvs = KeyValue.objects.filter(hostid=self.host, keyid=tmpkey)
        self.assertEqual(kvs[0].value, 'noob')
        tmpkey.delete()

    ###########################################################################
    def test_link_list(self):
        """ Listing links of a host through the REST interface """
        response = self.client.get('/api/host/hostrh/link/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEqual(ans['links'][0]['url'], 'http://localhost')
        self.assertEqual(ans['links'][0]['tag'], 'heur')

    ###########################################################################
    def test_link_get(self):
        """ Getting links of a host through the REST interface """
        response = self.client.get('/api/host/hostrh/link/heur/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEqual(ans['links'][0]['url'], 'http://localhost')
        self.assertEqual(ans['links'][0]['tag'], 'heur')

    ###########################################################################
    def test_link_update(self):
        """ Updating of links of a host through the REST interface """
        link = 'http://www.example.com'
        response = self.client.post('/api/host/hostrh/link/heur/%s' % link)
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'updated')
        self.assertEqual(ans['links'][0]['url'], 'http://www.example.com')

    ###########################################################################
    def test_link_set(self):
        """ Setting links of a host through the REST interface """
        link = 'http://www.example.org'
        response = self.client.post('/api/host/hostrh/link/chain/%s' % link)
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'created')
        self.assertEqual(ans['links'][0]['url'], 'http://www.example.org')

    ###########################################################################
    def test_link_delete(self):
        """ Deleting links of a host through the REST interface """
        response = self.client.delete('/api/host/hostrh/link/heur/')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'deleted')
        los = Links.objects.filter(hostid=self.host)
        self.assertEqual(len(los), 0)

    ###########################################################################
    def test_key_detail(self):
        """ Details of AllowedKeys through the REST interface """
        response = self.client.get('/api/key/rhkey')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['key']['key'], 'rhkey')
        self.assertEquals(ans['key']['desc'], 'testkey')

    ###########################################################################
    def test_key_by_id(self):
        """ Details of AllowedKeys using key id through the REST interface """
        response = self.client.get('/api/key/rhkey')
        self.assertEquals(response.status_code, 200)
        a = json.loads(response.content.decode())
        keyid = a['key']['id']
        response = self.client.get('/api/key/%d' % keyid)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['key']['key'], 'rhkey')
        self.assertEquals(ans['key']['desc'], 'testkey')

    ###########################################################################
    def test_key_restricted(self):
        """ Details of RestrictedKey through the REST interface """
        rvals = ['yes', 'no', 'maybe']
        rk = AllowedKey(key='restr', validtype=1, restrictedFlag=True)
        rk.save()
        avs = {}
        for i in rvals:
            avs[i] = RestrictedValue(keyid=rk, value=i)
            avs[i].save()
        response = self.client.get('/api/key/restr')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertIn(ans['key']['permitted_values'][0]['value'], rvals)
        for i in avs:
            avs[i].delete()
        rk.delete()

    ###########################################################################
    def test_keyval_details(self):
        """ Show the details of a single keyvalue"""
        response = self.client.get('/api/host/hostrh/')
        self.assertEquals(response.status_code, 200)
        a = json.loads(response.content.decode())
        keyid = a['host']['keyvalues']['rhkey'][0]['id']
        response = self.client.get('/api/kval/%s/' % keyid)
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEquals(ans['result'], 'ok')
        self.assertEquals(ans['keyvalue']['value'], 'val')
        self.assertEquals(ans['keyvalue']['id'], keyid)
        self.assertEquals(ans['keyvalue']['host']['hostname'], 'hostrh')

    ###########################################################################
    def test_erroring_regexp(self):
        # Issue 36
        response = self.client.get('/api/query/rhkey=host/rhlist.defined')
        self.assertNotEquals(response.status_code, 404)


###############################################################################
class test_bare(TestCase):
    def setUp(self):
        self.client = Client()
        self.host = Host(hostname='hostcn')
        self.host.save()
        self.key = AllowedKey(key='cnkey', validtype=1, desc='testkey')
        self.key.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value='tbval')
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_hostcount(self):
        """ Show in bare the count of hosts that match a criteria """
        response = self.client.get('/bare/count/cnkey.defined/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['bare/hostcount.html', 'bare/base.html']
            )
        self.assertIn('1', str(response.content))

    ###########################################################################
    def test_hostlist(self):
        """ Show in bare the hosts that match a criteria """
        response = self.client.get('/bare/hostlist/cnkey.defined/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['bare/hostlist.html', 'bare/base.html']
            )

    ###########################################################################
    def test_hosttable(self):
        """ Show host table"""
        response = self.client.get('/bare/hostlist/hostcn/?print=cnkey')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['bare/hostlist.html', 'bare/base.html']
            )
        self.assertIn('tbval', str(response.content))

    ###########################################################################
    def test_host(self):
        """ Show a specific host"""
        response = self.client.get('/bare/host/hostcn')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['bare/host.html', 'bare/base.html']
            )

    ###########################################################################
    def test_keylist(self):
        """ Show in bare details about a key"""
        response = self.client.get('/bare/keylist/cnkey/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            [t.name for t in response.templates],
            ['bare/keylist.html', 'bare/base.html']
            )

    ###########################################################################
    def test_keylist_with_crit(self):
        """ Show in bare details about a key with criteria"""
        response = self.client.get('/bare/keylist/cnkey/cnkey.defined/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('tbval', str(response.content))
        self.assertEquals(
            [t.name for t in response.templates],
            ['bare/keylist.html', 'bare/base.html']
            )

    ###########################################################################
    def test_hostcmp(self):
        """ Show in bare details about all hosts that match a criteria """
        response = self.client.get('/bare/hostcmp/cnkey.defin/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            sorted([str(t.name) for t in response.templates]),
            sorted(['bare/base.html', 'bare/showall.html', 'bare/multihost.html'])
            )


###############################################################################
class test_calcKeylistVals(TestCase):
    def setUp(self):
        clearAKcache()
        self.key1 = AllowedKey(key='ckvkey1', validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key='ckvkey2', validtype=1)
        self.key2.save()
        self.host1 = Host(hostname='ckvhost1')
        self.host1.save()
        self.host2 = Host(hostname='ckvhost2')
        self.host2.save()
        self.kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value='foo')
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host1, keyid=self.key2, value='bar')
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.host2, keyid=self.key2, value='baz')
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
        qualifiers = parseQualifiers(['ckvkey1.undefined'])
        matches = getMatches(qualifiers)
        d = calcKeylistVals('ckvkey2', matches)
        self.assertEquals(d['key'], 'ckvkey2')
        self.assertEquals(d['numdef'], 1)
        self.assertEquals(d['numundef'], 0)
        self.assertEquals(d['pctdef'], 100.0)
        self.assertEquals(d['pctundef'], 0.0)
        self.assertEquals(d['total'], 1)
        self.assertEquals(d['numvals'], 1)
        self.assertEquals(d['vallist'], [(u'baz', 1, 100.0)])

    def test_another_key(self):
        d = calcKeylistVals('ckvkey1')
        self.assertEquals(d['key'], 'ckvkey1')
        self.assertEquals(d['numdef'], 1)
        self.assertEquals(d['numundef'], 1)
        self.assertEquals(d['pctdef'], 50.0)
        self.assertEquals(d['pctundef'], 50.0)
        self.assertEquals(d['total'], 2)
        self.assertEquals(d['numvals'], 1)
        self.assertEquals(d['vallist'], [(u'foo', 1, 100.0)])

    def test_simple_key(self):
        d = calcKeylistVals('ckvkey2')
        self.assertEquals(d['key'], 'ckvkey2')
        self.assertEquals(d['numdef'], 2)
        self.assertEquals(d['numundef'], 0)
        self.assertEquals(d['pctdef'], 100.0)
        self.assertEquals(d['pctundef'], 0.0)
        self.assertEquals(d['total'], 2)
        self.assertEquals(d['numvals'], 2)
        self.assertEquals(d['vallist'], [(u'bar', 1, 50.0), (u'baz', 1, 50.0)])

    def test_bad_key(self):
        with self.assertRaises(HostinfoException):
            calcKeylistVals('badkey')


###############################################################################
class test_hostData(TestCase):
    def setUp(self):
        clearAKcache()
        self.key1 = AllowedKey(key='hdfkey1', validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key='hdfkey2', validtype=1)
        self.key2.save()
        self.host1 = Host(hostname='hdfhost1')
        self.host1.save()
        self.host2 = Host(hostname='hdfhost2')
        self.host2.save()
        self.host3 = Host(hostname='hdfhost3')
        self.host3.save()
        self.kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value='foo')
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host1, keyid=self.key2, value='bar')
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.host3, keyid=self.key2, value='baz')
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
        result = hostData('fred')
        self.assertEquals(result['count'], 3)
        self.assertEquals(result['criteria'], '')
        self.assertEquals(result['title'], '')
        self.assertEquals(result['csvavailable'], '/hostinfo/csv/')
        self.assertEquals(result['options'], '')
        self.assertEquals(result['order'], None)
        self.assertEquals(result['printers'], [])
        self.assertEquals(result['user'], 'fred')
        self.assertEquals(result['hostlist'][0]['hostname'], 'hdfhost1')
        self.assertEquals(result['hostlist'][1]['hostname'], 'hdfhost2')
        self.assertEquals(result['hostlist'][2]['hostname'], 'hdfhost3')

    def test_double_criteria(self):
        result = hostData('fred', criteria=['hdfkey1.defined', 'hdfhost1.hostre'])
        self.assertEquals(result['count'], 1)
        self.assertEquals(result['criteria'], 'hdfkey1.defined/hdfhost1.hostre')
        self.assertEquals(result['title'], 'hdfkey1.defined AND hdfhost1.hostre')
        self.assertEquals(result['csvavailable'], '/hostinfo/csv/hdfkey1.defined/hdfhost1.hostre')
        self.assertEquals(result['options'], '')
        self.assertEquals(result['order'], None)
        self.assertEquals(result['printers'], [])
        self.assertEquals(result['user'], 'fred')
        self.assertEquals(result['hostlist'][0]['hostname'], 'hdfhost1')
        self.assertEquals(result['hostlist'][0]['hostview'], [(u'hdfkey1', [self.kv1]), (u'hdfkey2', [self.kv2])])

    def test_single_criteria(self):
        result = hostData('fred', criteria=['hdfkey1.defined'])
        self.assertEquals(result['count'], 1)
        self.assertEquals(result['criteria'], 'hdfkey1.defined')
        self.assertEquals(result['title'], 'hdfkey1.defined')
        self.assertEquals(result['csvavailable'], '/hostinfo/csv/hdfkey1.defined')
        self.assertEquals(result['options'], '')
        self.assertEquals(result['order'], None)
        self.assertEquals(result['printers'], [])
        self.assertEquals(result['user'], 'fred')
        self.assertEquals(result['hostlist'][0]['hostname'], 'hdfhost1')

    def test_printers(self):
        result = hostData('fred', criteria=['hdfkey2.defined'], printers=['hdfkey2'])
        self.assertEquals(result['count'], 2)
        self.assertEquals(result['criteria'], 'hdfkey2.defined')
        self.assertEquals(result['title'], 'hdfkey2.defined')
        self.assertEquals(result['csvavailable'], '/hostinfo/csv/hdfkey2.defined')
        self.assertEquals(result['options'], '')
        self.assertEquals(result['order'], None)
        self.assertEquals(result['printers'], ['hdfkey2'])
        self.assertEquals(result['user'], 'fred')
        self.assertEquals(result['hostlist'][0]['hostview'], [(u'hdfkey2', [self.kv2])])
        self.assertEquals(result['hostlist'][1]['hostview'], [(u'hdfkey2', [self.kv3])])

    def test_order(self):
        host1 = Host(hostname='hdfhost4')
        host1.save()
        kv1 = KeyValue(hostid=host1, keyid=self.key1, value='alpha')
        kv1.save()
        host2 = Host(hostname='hdfhost5')
        host2.save()
        kv2 = KeyValue(hostid=host2, keyid=self.key1, value='zomega')
        kv2.save()

        result = hostData('fred', criteria=['hdfkey1.defined'], order='hdfkey1')
        self.assertEquals(result['count'], 3)
        self.assertEquals(result['criteria'], 'hdfkey1.defined')
        self.assertEquals(result['title'], 'hdfkey1.defined')
        self.assertEquals(result['csvavailable'], '/hostinfo/csv/hdfkey1.defined')
        self.assertEquals(result['options'], '')
        self.assertEquals(result['order'], 'hdfkey1')
        self.assertEquals(result['printers'], [])
        self.assertEquals(result['user'], 'fred')
        self.assertEquals(result['hostlist'][0]['hostname'], 'hdfhost4')
        self.assertEquals(result['hostlist'][1]['hostname'], 'hdfhost1')
        self.assertEquals(result['hostlist'][2]['hostname'], 'hdfhost5')
        kv1.delete()
        kv2.delete()
        host1.delete()
        host2.delete()


###############################################################################
class test_version(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_version(self):
        response = self.client.get('/_version')
        self.assertEquals(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertTrue(len(ans['version']) > 1)

# EOF
