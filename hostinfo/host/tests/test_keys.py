""" Key based tests for hostinfo"""

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

from django.test import TestCase

from host.models import Host, AllowedKey, KeyValue, RestrictedValue
from host.models import HostinfoException, ReadonlyValueException
from host.models import RestrictedValueException
from host.models import addKeytoHost
from host.models import clearAKcache
from host.models import getHost, getAK


###############################################################################
class test_SingleKey(TestCase):
    """Test operations on a single values key"""

    def setUp(self):
        clearAKcache()
        self.host = Host(hostname="host")
        self.host.save()
        self.key = AllowedKey(key="single", validtype=1)
        self.key.save()
        self.num = AllowedKey(key="number", validtype=1, numericFlag=True)
        self.num.save()

    ###########################################################################
    def tearDown(self):
        self.num.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def checkValue(self, host, key):
        """ TODO """
        keyid = getAK(key)
        hostid = getHost(host)
        kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
        return kv[0].value

    ###########################################################################
    def checkNumValue(self, host, key):
        """ TODO """
        keyid = getAK(key)
        hostid = getHost(host)
        kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
        return kv[0].numvalue

    ###########################################################################
    def test_blank_value(self):
        """Test that blank and whitespace only values fail"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="host", key="single", value="")
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="host", key="single", value="  ")

    ###########################################################################
    def test_numeric_nonnumeric(self):
        """Test numeric keys with a non-numeric value"""
        addKeytoHost(host="host", key="number", value="a")
        self.assertEqual(self.checkValue("host", "number"), "a")
        self.assertIsNone(self.checkNumValue("host", "number"))

    ###########################################################################
    def test_numeric_numeric(self):
        """Test numeric keys with a numeric value"""
        addKeytoHost(host="host", key="number", value="100")
        self.assertEqual(self.checkValue("host", "number"), "100")
        self.assertEqual(self.checkNumValue("host", "number"), 100)

    ###########################################################################
    def test_adds(self):
        """Test adding a simple value"""
        addKeytoHost(host="host", key="single", value="a")
        self.assertEqual(self.checkValue("host", "single"), "a")

    ###########################################################################
    def test_readonly(self):
        """Test modifications to readonly keys"""
        rokey = AllowedKey(key="ro", validtype=1, readonlyFlag=True)
        rokey.save()
        with self.assertRaises(ReadonlyValueException):
            addKeytoHost(host="host", key="ro", value="b")
        addKeytoHost(host="host", key="ro", value="a", readonlyFlag=True)
        self.assertEqual(self.checkValue("host", "ro"), "a")
        rokey.delete()

    ###########################################################################
    def test_addtwice(self):
        """Test adding the same value again"""
        addKeytoHost(host="host", key="single", value="a")
        addKeytoHost(host="host", key="single", value="a")
        self.assertEqual(self.checkValue("host", "single"), "a")

    ###########################################################################
    def test_changevalue(self):
        """Add a value without override"""
        addKeytoHost(host="host", key="single", value="a")
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="host", key="single", value="b")
        self.assertEqual(self.checkValue("host", "single"), "a")

    ###########################################################################
    def test_override(self):
        """Add a value with override"""
        addKeytoHost(host="host", key="single", value="a")
        addKeytoHost(host="host", key="single", value="b", updateFlag=True)
        self.assertEqual(self.checkValue("host", "single"), "b")

    ###########################################################################
    def test_nohost(self):
        """Test adding to a host that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="hostnot", key="single", value="b")

    ###########################################################################
    def test_append(self):
        """Test to make sure we can't append"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="host", key="single", value="a", appendFlag=True)

    ###########################################################################
    def test_badkey(self):
        """Test adding to a key that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="host", key="fake", value="b")


###############################################################################
class test_ListKey(TestCase):
    """Test operations on a list of values key"""

    def setUp(self):
        clearAKcache()
        self.host = Host(hostname="host")
        self.host.save()
        self.key = AllowedKey(key="lk_list", validtype=2)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def checkValue(self, host, key):
        """ TODO """
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
        """Test adding a simple value"""
        addKeytoHost(host="host", key="lk_list", value="a")
        self.assertEqual(self.checkValue("host", "lk_list"), "a")

    ###########################################################################
    def test_readonly(self):
        """Test modifications to readonly keys"""
        rokey = AllowedKey(key="ro", validtype=1, readonlyFlag=True)
        rokey.save()
        addKeytoHost(host="host", key="ro", value="a", readonlyFlag=True)
        addKeytoHost(host="host", key="ro", value="a")
        self.assertEqual(self.checkValue("host", "ro"), "a")
        rokey.delete()

    ###########################################################################
    def test_addtwice(self):
        """Test adding the same value again"""
        addKeytoHost(host="host", key="lk_list", value="a")
        addKeytoHost(host="host", key="lk_list", value="a")
        self.assertEqual(self.checkValue("host", "lk_list"), "a")

    ###########################################################################
    def test_changevalue(self):
        """Add a value without override"""
        addKeytoHost(host="host", key="lk_list", value="a")
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="host", key="lk_list", value="b")
        self.assertEqual(self.checkValue("host", "lk_list"), "a")

    ###########################################################################
    def test_override(self):
        """Add a value with override"""
        addKeytoHost(host="host", key="lk_list", value="a")
        addKeytoHost(host="host", key="lk_list", value="b", updateFlag=True)
        self.assertEqual(self.checkValue("host", "lk_list"), "b")

    ###########################################################################
    def test_nohost(self):
        """Test adding to a host that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="hostnot", key="lk_list", value="b")

    ###########################################################################
    def test_append(self):
        """Test to make sure we can append"""
        addKeytoHost(host="host", key="lk_list", value="a")
        addKeytoHost(host="host", key="lk_list", value="b", appendFlag=True)
        self.assertEqual(self.checkValue("host", "lk_list"), ["a", "b"])

    ###########################################################################
    def test_append_twice(self):
        """Test to make sure we can't append the same value twice"""
        addKeytoHost(host="host", key="lk_list", value="a")
        addKeytoHost(host="host", key="lk_list", value="a", appendFlag=True)
        self.assertEqual(self.checkValue("host", "lk_list"), "a")

    ###########################################################################
    def test_badkey(self):
        """Test adding to a key that doesn't exist"""
        with self.assertRaises(HostinfoException):
            addKeytoHost(host="host", key="fake", value="b")


###############################################################################
class test_Restricted(TestCase):
    """Test operations on a restricted key"""

    def setUp(self):
        clearAKcache()
        self.host = Host(hostname="host")
        self.host.save()
        self.key = AllowedKey(key="restr", validtype=1, restrictedFlag=True)
        self.key.save()
        self.rv = RestrictedValue(keyid=self.key, value="allowed")
        self.rv.save()

    ###########################################################################
    def tearDown(self):
        self.rv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_adds(self):
        """Test that we can add a key of the appropriate value
        and that it raises an exception if we add the wrong value
        """
        with self.assertRaises(RestrictedValueException):
            addKeytoHost(host="host", key="restr", value="forbidden")
        addKeytoHost(host="host", key="restr", value="allowed")


###############################################################################
class test_DateKey(TestCase):
    """Test operations on a date based key"""

    def setUp(self):
        clearAKcache()
        self.host = Host(hostname="host")
        self.host.save()
        self.key = AllowedKey(key="date", validtype=3)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def checkValue(self, host, key):
        """ TODO """
        keyid = getAK(key)
        hostid = getHost(host)
        kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
        return kv[0].value

    ###########################################################################
    def test_adds(self):
        """Test adding a simple value"""
        addKeytoHost(host="host", key="date", value="2012-12-31")
        self.assertEqual(self.checkValue("host", "date"), "2012-12-31")


# EOF
