""" Test rig for bare interface to hostinfo"""

# Written by Dougal Scott <dougal.scott@gmail.com>

#    Copyright (C) 2022 Dougal Scott
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

from host.models import Host, AllowedKey
from host.models import KeyValue


###############################################################################
class test_bare(TestCase):
    """ Test Bare interface """
    def setUp(self):
        self.client = Client()
        self.host = Host(hostname="hostcn")
        self.host.save()
        self.key = AllowedKey(key="cnkey", validtype=1, desc="testkey")
        self.key.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value="tbval")
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_hostcount(self):
        """Show in bare the count of hosts that match a criteria"""
        response = self.client.get("/bare/count/cnkey.defined/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [t.name for t in response.templates],
            ["bare/hostcount.html", "bare/base.html"],
        )
        self.assertIn("1", str(response.content))

    ###########################################################################
    def test_hostlist(self):
        """Show in bare the hosts that match a criteria"""
        response = self.client.get("/bare/hostlist/cnkey.defined/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [t.name for t in response.templates],
            ["bare/hostlist.html", "bare/base.html"],
        )

    ###########################################################################
    def test_hosttable(self):
        """Show host table"""
        response = self.client.get("/bare/hostlist/hostcn/?print=cnkey/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [t.name for t in response.templates],
            ["bare/hostlist.html", "bare/base.html"],
        )
        self.assertIn("tbval", str(response.content))

    ###########################################################################
    def test_host(self):
        """Show a specific host"""
        response = self.client.get("/bare/host/hostcn/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [t.name for t in response.templates], ["bare/host.html", "bare/base.html"]
        )

    ###########################################################################
    def test_keylist(self):
        """Show in bare details about a key"""
        response = self.client.get("/bare/keylist/cnkey/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [_.name for _ in response.templates],
            ["bare/keylist.html", "bare/base.html"],
        )

    ###########################################################################
    def test_keylist_with_crit(self):
        """Show in bare details about a key with criteria"""
        response = self.client.get("/bare/keylist/cnkey/cnkey.defined/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("tbval", str(response.content))
        self.assertEqual(
            [t.name for t in response.templates],
            ["bare/keylist.html", "bare/base.html"],
        )

    ###########################################################################
    def test_hostcmp(self):
        """Show in bare details about all hosts that match a criteria"""
        response = self.client.get("/bare/hostcmp/cnkey.defin/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted([str(t.name) for t in response.templates]),
            sorted(["bare/base.html", "bare/showall.html", "bare/multihost.html"]),
        )


# EOF
