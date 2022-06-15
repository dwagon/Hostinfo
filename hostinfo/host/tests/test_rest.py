""" Test rig for REST interface to hostinfo"""

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

import json

from django.test import TestCase
from django.test.client import Client

from host.models import Host, HostAlias, AllowedKey, RestrictedValue, Links
from host.models import clearAKcache
from host.models import addKeytoHost, KeyValue


###############################################################################
class test_restHost_keylist(TestCase):
    """ Test keylist through REST """
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.host = Host(hostname="hostrhkl")
        self.host.save()
        self.key = AllowedKey(key="rhkeykl", validtype=1, desc="testkey")
        self.key.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value="val")
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_keylist(self):
        """ Test listing of keys """
        response = self.client.get("/api/keylist/rhkeykl/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["key"], "rhkeykl")
        self.assertEqual(ans["numdef"], 1)
        self.assertEqual(ans["numvals"], 1)
        self.assertEqual(ans["total"], 1)

    ###########################################################################
    def test_keylist_criteria(self):
        """ List keys with an additional criteria """
        response = self.client.get("/api/keylist/rhkeykl/rhkeykl.defined/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["key"], "rhkeykl")
        self.assertEqual(ans["numdef"], 1)
        self.assertEqual(ans["vallist"], [["val", 1, 100.0]])


###############################################################################
class test_restHost_query(TestCase):
    """ Query through REST interface """
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.host = Host(hostname="hostrhq")
        self.host.save()
        self.key = AllowedKey(key="rhqkey", validtype=1, desc="testkey")
        self.key.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value="val")
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_query(self):
        """ Do a query """
        response = self.client.get("/api/query/rhqkey=val/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "1 matching hosts")
        self.assertEqual(ans["hosts"][0]["hostname"], "hostrhq")
        self.assertSequenceEqual(
            sorted(ans["hosts"][0].keys()), sorted(["id", "hostname", "url"])
        )

    ###########################################################################
    def test_query_origin(self):
        """ Test origin output """
        response = self.client.get("/api/query/rhqkey=val/?origin=True")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertSequenceEqual(
            sorted(ans["hosts"][0].keys()), sorted(["id", "hostname", "url", "origin"])
        )

    ###########################################################################
    def test_query_multi(self):
        response = self.client.get(
            "/api/query/rhqkey=val/?aliases=True&dates=True&links=True"
        )
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertSequenceEqual(
            sorted(ans["hosts"][0].keys()),
            sorted(
                [
                    "id",
                    "hostname",
                    "url",
                    "aliases",
                    "createdate",
                    "modifieddate",
                    "links",
                ]
            ),
        )

    ###########################################################################
    def test_query_keys(self):
        response = self.client.get("/api/query/rhqkey=val/?keys=rhqkey")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "1 matching hosts")
        self.assertEqual(ans["hosts"][0]["hostname"], "hostrhq")
        self.assertEqual(ans["hosts"][0]["keyvalues"]["rhqkey"][0]["value"], "val")

    ###########################################################################
    def test_query_multikeys(self):
        k2 = AllowedKey(key="rhqkey2", validtype=1, desc="testkey2")
        k2.save()
        kv2 = KeyValue(hostid=self.host, keyid=k2, value="val2")
        kv2.save()
        response = self.client.get("/api/query/rhqkey=val/?keys=rhqkey,rhqkey2")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "1 matching hosts")
        self.assertEqual(ans["hosts"][0]["hostname"], "hostrhq")
        self.assertEqual(ans["hosts"][0]["keyvalues"]["rhqkey"][0]["value"], "val")
        self.assertEqual(ans["hosts"][0]["keyvalues"]["rhqkey2"][0]["value"], "val2")
        kv2.delete()
        k2.delete()

    ###########################################################################
    def test_bad_query(self):
        response = self.client.get("/api/query/badkey=val/")
        self.assertEqual(response.status_code, 406)
        ans = json.loads(response.content.decode())
        self.assertIn("badkey", ans["error"])


###############################################################################
class test_restHost(TestCase):
    def setUp(self):
        self.client = Client()
        self.host = Host(hostname="hostrh")
        self.host.save()
        self.key = AllowedKey(key="rhkey", validtype=1, desc="testkey")
        self.key.save()
        self.listkey = AllowedKey(key="rhlist", validtype=2, desc="list key")
        self.listkey.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value="val")
        self.kv.save()
        self.alias1 = HostAlias(hostid=self.host, alias="rhalias")
        self.alias1.save()
        self.alias2 = HostAlias(hostid=self.host, alias="rhalias2")
        self.alias2.save()
        self.link = Links(hostid=self.host, url="http://localhost", tag="heur")
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
        """ Test creation of host through REST interface """
        data = {"origin": "testorigin"}
        response = self.client.post(
            "/api/host/noahsark/", data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["host"]["hostname"], "noahsark")
        host = Host.objects.get(hostname="noahsark")
        self.assertEqual(host.origin, "testorigin")
        host.delete()

    ###########################################################################
    def test_hostlist(self):
        """ Test listing of hosts through REST interface """
        response = self.client.get("/api/host/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "1 hosts")
        self.assertEqual(ans["hosts"][0]["hostname"], "hostrh")

    ###########################################################################
    def test_host_byid(self):
        """Getting a host by its id"""
        response = self.client.get("/api/host/hostrh/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        hostid = ans["host"]["id"]
        response = self.client.get(f"/api/host/{hostid}/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["host"]["hostname"], "hostrh")

    ###########################################################################
    def test_hostdetails(self):
        """ Getting a hsot by its hostname """
        response = self.client.get("/api/host/hostrh/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["host"]["keyvalues"]["rhkey"][0]["value"], "val")

    ###########################################################################
    def test_alias_details(self):
        """ Get host details by its alias """
        response = self.client.get("/api/host/rhalias/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["host"]["keyvalues"]["rhkey"][0]["value"], "val")

    ###########################################################################
    def test_missing_details(self):
        """ Test asking for a host that doesn't exist """
        response = self.client.get("/api/host/badhost/")
        self.assertEqual(response.status_code, 404)

    ###########################################################################
    def test_list_aliases(self):
        """ List all aliases """
        response = self.client.get("/api/alias/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["aliases"][0]["host"]["hostname"], "hostrh")
        self.assertIn(ans["aliases"][0]["alias"], ["rhalias", "rhalias2"])

    ###########################################################################
    def test_list_hostalias(self):
        response = self.client.get("/api/host/hostrh/alias/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        al = [a["alias"] for a in ans["aliases"]]
        self.assertEqual(sorted(al), ["rhalias", "rhalias2"])

    ###########################################################################
    def test_get_alias(self):
        response = self.client.get("/api/host/hostrh/alias/rhalias/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["aliases"][0]["alias"], "rhalias")

    ###########################################################################
    def test_set_alias(self):
        response = self.client.post("/api/host/hostrh/alias/rhalias3/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        aliases = HostAlias.objects.filter(hostid=self.host, alias="rhalias3")
        self.assertEqual(len(aliases), 1)

    ###########################################################################
    def test_set_duplicate_alias(self):
        response = self.client.post("/api/host/hostrh/alias/rhalias2/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "duplicate")
        aliases = HostAlias.objects.filter(hostid=self.host, alias="rhalias2")
        self.assertEqual(len(aliases), 1)

    ###########################################################################
    def test_delete_alias(self):
        """ Delete an alias """
        response = self.client.delete("/api/host/hostrh/alias/rhalias2/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "deleted")
        aliases = HostAlias.objects.filter(hostid=self.host, alias="rhalias2")
        self.assertEqual(len(aliases), 0)

    ###########################################################################
    def test_list_keys(self):
        """Test the listing of keys through the REST interface"""
        response = self.client.get("/api/host/hostrh/key/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["keyvalues"][0]["value"], "val")
        self.assertEqual(ans["keyvalues"][0]["key"], "rhkey")

    ###########################################################################
    def test_get_keyval(self):
        """Test the getting of keys through the REST interface"""
        response = self.client.get("/api/host/hostrh/key/rhkey/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["keyvalues"][0]["value"], "val")
        self.assertEqual(ans["keyvalues"][0]["key"], "rhkey")

    ###########################################################################
    def test_set_keyval(self):
        """Test the setting of keys through the REST interface"""
        response = self.client.post("/api/host/hostrh/key/rhkey/baz/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "updated")
        self.assertEqual(ans["keyvalues"][0]["value"], "baz")
        self.assertEqual(ans["keyvalues"][0]["key"], "rhkey")

    ###########################################################################
    def test_delete_keyval(self):
        """ Delete a key value pair"""
        response = self.client.delete("/api/host/hostrh/key/rhkey/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "deleted")
        kvs = KeyValue.objects.filter(hostid=self.host, keyid=self.key)
        self.assertEqual(len(kvs), 0)

    ###########################################################################
    def test_delete_from_list(self):
        """Delete values from a list through REST"""
        lkey = AllowedKey(key="rhlist2", validtype=2, desc="list key for deleting")
        lkey.save()
        addKeytoHost(host="hostrh", key="rhlist2", value="a")
        addKeytoHost(host="hostrh", key="rhlist2", value="b", appendFlag=True)
        addKeytoHost(host="hostrh", key="rhlist2", value="c", appendFlag=True)
        response = self.client.delete("/api/host/hostrh/key/rhlist2/b/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "deleted")
        kvs = KeyValue.objects.filter(hostid=self.host, keyid=lkey)
        self.assertEqual(len(kvs), 2)
        lkey.delete()

    ###########################################################################
    def test_append_keyval(self):
        """Append values to a list through REST"""
        response = self.client.post("/api/host/hostrh/key/rhlist/alpha/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/api/host/hostrh/key/rhlist/beta/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "appended")
        kvs = KeyValue.objects.filter(hostid=self.host, keyid=self.listkey)
        self.assertEqual(len(kvs), 2)

    ###########################################################################
    def test_create_keyval(self):
        """ Test creation of a key value pair """
        tmpkey = AllowedKey(key="tmprhkey", validtype=1)
        tmpkey.save()
        response = self.client.post("/api/host/hostrh/key/tmprhkey/noob/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "created")
        kvs = KeyValue.objects.filter(hostid=self.host, keyid=tmpkey)
        self.assertEqual(kvs[0].value, "noob")
        tmpkey.delete()

    ###########################################################################
    def test_link_list(self):
        """Listing links of a host through the REST interface"""
        response = self.client.get("/api/host/hostrh/link/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["links"][0]["url"], "http://localhost")
        self.assertEqual(ans["links"][0]["tag"], "heur")

    ###########################################################################
    def test_link_get(self):
        """Getting links of a host through the REST interface"""
        response = self.client.get("/api/host/hostrh/link/heur/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["links"][0]["url"], "http://localhost")
        self.assertEqual(ans["links"][0]["tag"], "heur")

    ###########################################################################
    def test_link_update(self):
        """Updating of links of a host through the REST interface"""
        link = "http://www.example.com"
        response = self.client.post(f"/api/host/hostrh/link/heur/{link}/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "updated")
        self.assertEqual(ans["links"][0]["url"], "http://www.example.com")

    ###########################################################################
    def test_link_set(self):
        """Setting links of a host through the REST interface"""
        link = "http://www.example.org"
        response = self.client.post(f"/api/host/hostrh/link/chain/{link}/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "created")
        self.assertEqual(ans["links"][0]["url"], "http://www.example.org")

    ###########################################################################
    def test_link_delete(self):
        """Deleting links of a host through the REST interface"""
        response = self.client.delete("/api/host/hostrh/link/heur/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "deleted")
        los = Links.objects.filter(hostid=self.host)
        self.assertEqual(len(los), 0)

    ###########################################################################
    def test_key_detail(self):
        """Details of AllowedKeys through the REST interface"""
        response = self.client.get("/api/key/rhkey/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["key"]["key"], "rhkey")
        self.assertEqual(ans["key"]["desc"], "testkey")

    ###########################################################################
    def test_key_by_id(self):
        """Details of AllowedKeys using key id through the REST interface"""
        response = self.client.get("/api/key/rhkey/")
        self.assertEqual(response.status_code, 200)
        a = json.loads(response.content.decode())
        keyid = a["key"]["id"]
        response = self.client.get(f"/api/key/{keyid}/")
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["key"]["key"], "rhkey")
        self.assertEqual(ans["key"]["desc"], "testkey")

    ###########################################################################
    def test_key_restricted(self):
        """Details of RestrictedKey through the REST interface"""
        rvals = ["yes", "no", "maybe"]
        rk = AllowedKey(key="restr", validtype=1, restrictedFlag=True)
        rk.save()
        avs = {}
        for i in rvals:
            avs[i] = RestrictedValue(keyid=rk, value=i)
            avs[i].save()
        response = self.client.get("/api/key/restr/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertIn(ans["key"]["permitted_values"][0]["value"], rvals)
        for _, vals in avs.items():
            vals.delete()
        rk.delete()

    ###########################################################################
    def test_keyval_details(self):
        """Show the details of a single keyvalue"""
        response = self.client.get("/api/host/hostrh/")
        self.assertEqual(response.status_code, 200)
        a = json.loads(response.content.decode())
        keyid = a["host"]["keyvalues"]["rhkey"][0]["id"]
        response = self.client.get(f"/api/kval/{keyid}/")
        self.assertEqual(response.status_code, 200)
        ans = json.loads(response.content.decode())
        self.assertEqual(ans["result"], "ok")
        self.assertEqual(ans["keyvalue"]["value"], "val")
        self.assertEqual(ans["keyvalue"]["id"], keyid)
        self.assertEqual(ans["keyvalue"]["host"]["hostname"], "hostrh")

    ###########################################################################
    def test_erroring_regexp(self):
        """ Issue 36"""
        response = self.client.get("/api/query/rhkey=host/rhlist.defined/")
        self.assertNotEqual(response.status_code, 404)


# EOF
