""" Test rig for URL interface to hostinfo"""

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
from django.test.client import Client
from django.contrib.auth.models import User

from host.models import Host, HostAlias, KeyValue, RestrictedValue, Links
from host.models import clearAKcache, AllowedKey


###############################################################################
class test_url_hostmerge(TestCase):
    """ Test /hostmerge API """
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.user = User.objects.create_user("test", "", "passwd")
        self.user.save()
        self.host1 = Host(hostname="merge1")
        self.host1.save()
        self.host2 = Host(hostname="merge2")
        self.host2.save()
        self.key = AllowedKey(key="mergekey", validtype=1)
        self.key.save()
        self.list = AllowedKey(key="mergelist", validtype=2)
        self.list.save()
        self.kv = KeyValue(hostid=self.host1, keyid=self.key, value="foo")
        self.kv.save()
        self.lv0 = KeyValue(hostid=self.host1, keyid=self.list, value="a")
        self.lv0.save()
        self.lv1 = KeyValue(hostid=self.host1, keyid=self.list, value="b")
        self.lv1.save()
        self.lv2 = KeyValue(hostid=self.host2, keyid=self.list, value="c")
        self.lv2.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.lv0.delete()
        self.lv1.delete()
        self.lv2.delete()
        self.user.delete()
        self.host1.delete()
        self.host2.delete()
        self.key.delete()
        self.list.delete()

    ###########################################################################
    def test_merge_form(self):
        """Ask for the host merge form"""
        self.client.login(username="test", password="passwd")
        response = self.client.get("/hostinfo/hostmerge/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(
                [
                    _.name
                    for _ in response.templates
                    if "django/forms" not in _.name
                ]
            ),
            sorted(["host/hostmerge.template", "host/base.html"]),
        )

    ###########################################################################
    def test_merge_form_submit(self):
        """Submit the host merge form"""
        self.client.login(username="test", password="passwd")
        response = self.client.post(
            "/hostinfo/hostmerge/",
            {"srchost": "merge1", "dsthost": "merge2"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted([t.name for t in response.templates]),
            sorted(
                [
                    "host/hostmerge.template",
                    "host/base.html",
                    "host/hostmerging.template",
                ]
            ),
        )
        self.assertIn(b'action="/hostinfo/hostmerge/merge1/merge2"', response.content)

    ###########################################################################
    def test_do_merge(self):
        """Send answers to the host merge form"""
        self.client.login(username="test", password="passwd")
        response = self.client.post(
            "/hostinfo/hostmerge/merge1/merge2",
            {
                "_srchost": "merge1",
                "_dsthost": "merge2",
                "_hostmerging": True,
                "mergekey": "src",
                "mergelist": "src",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("host/hostmerge.template")
        self.assertTemplateUsed("host/base.template")
        self.assertTemplateUsed("host/hostmergeing.template")

        host = Host.objects.filter(hostname="merge1")
        self.assertEqual(len(host), 0)

        host = Host.objects.filter(hostname="merge2")
        self.assertEqual(len(host), 1)

        kv = KeyValue.objects.filter(hostid=self.host2, keyid=self.key)
        self.assertEqual(kv[0].value, "foo")

        kvs = KeyValue.objects.filter(hostid=self.host2, keyid=self.list)
        self.assertEqual(len(kvs), 2)


###############################################################################
class test_url_hostrename(TestCase):
    """ Rename a host """
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.user = User.objects.create_user("test", "", "passwd")
        self.user.save()
        self.host = Host(hostname="urenamehost1")
        self.host.save()

    ###########################################################################
    def tearDown(self):
        self.user.delete()
        self.host.delete()

    ###########################################################################
    def test_do_rename(self):
        """Send answers to the host rename form"""
        self.client.login(username="test", password="passwd")
        response = self.client.post(
            "/hostinfo/hostrename/",
            {"srchost": "urenamehost1", "dsthost": "urenamed"},
            follow=True,
        )

        self.assertIn(
            b"urenamehost1 has been successfully renamed to urenamed", response.content
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("host/hostrename.template", [_.name for _ in response.templates])
        self.assertIn("host/base.html", [_.name for _ in response.templates])
        host = Host.objects.filter(hostname="urenamehost1")
        self.assertEqual(len(host), 0)
        host = Host.objects.filter(hostname="urenamed")
        self.assertEqual(len(host), 1)

    ###########################################################################
    def test_blank_form(self):
        """Ask for the host rename form"""
        self.client.login(username="test", password="passwd")
        response = self.client.get("/hostinfo/hostrename/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(
                [
                    _.name
                    for _ in response.templates
                    if "django/forms" not in _.name
                ]
            ),
            sorted(["host/hostrename.template", "host/base.html"]),
        )


###############################################################################
class test_url_index(TestCase):
    """ Test index """
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.client = Client()

    ###########################################################################
    def tearDown(self):
        pass

    ###########################################################################
    def test_base(self):
        """ Test index """
        response = self.client.get("/hostinfo/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/index.template", "host/base.html"],
        )


###############################################################################
class test_url_handlePost(TestCase):
    """ handle Post"""
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.key = AllowedKey(key="postkey", validtype=1)
        self.key.save()
        self.host = Host(hostname="posthost")
        self.host.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value="foo")
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()

    ###########################################################################
    def test_hostname(self):
        """ Test POSTing hostname """
        response = self.client.post(
            "/hostinfo/handlePost/", data={"hostname": "posthost"}
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            "/hostinfo/handlePost/", data={"hostname": "posthost"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted([t.name for t in response.templates]),
            ["host/base.html", "host/host.template", "host/showall.template"],
        )


###############################################################################
class test_url_keylist(TestCase):
    """Test views doKeylist function"""

    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.key = AllowedKey(key="urlkey", validtype=1)
        self.key.save()
        self.host = Host(hostname="urlhost1")
        self.host.save()
        self.host2 = Host(hostname="urlhost2")
        self.host2.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value="foo")
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.key.delete()
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_withkey(self):
        """ Test with key """
        response = self.client.get("/hostinfo/keylist/urlkey/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            sorted([t.name for t in response.templates]),
            ["host/base.html", "host/keylist.template"],
        )
        self.assertEqual(response.context["key"], "urlkey")
        self.assertEqual(response.context["total"], 2)  # Number of hosts
        self.assertEqual(response.context["numvals"], 1)  # Number of different values
        self.assertEqual(response.context["pctundef"], 50)  # % hosts with key not def
        self.assertEqual(response.context["numundef"], 1)  # Num hosts with key not def
        self.assertEqual(response.context["pctdef"], 50)  # % hosts with key defined
        self.assertEqual(response.context["numdef"], 1)  # Num hosts with key defined
        self.assertEqual(
            response.context["vallist"], [("foo", 1, 100)]
        )  # Key, Value, Percentage

    ###########################################################################
    def test_badkey(self):
        """ Test with a bad key """
        response = self.client.get("/hostinfo/keylist/badkey/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" in response.context)
        self.assertEqual(
            sorted([t.name for t in response.templates]),
            ["host/base.html", "host/keylist.template"],
        )


###############################################################################
class test_url_rvlist(TestCase):
    r"""Test doRestrValList function and /hostinfo/rvlist url
    (r'^rvlist/(?P<key>\S+)/$', 'doRestrValList'),
    (r'^rvlist/(?P<key>\S+)/(?P<mode>\S+)$', 'doRestrValList'),
    """

    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.key = AllowedKey(key="rvlkey", validtype=1, restrictedFlag=True)
        self.key.save()
        self.rv1 = RestrictedValue(keyid=self.key, value="good")
        self.rv1.save()
        self.rv2 = RestrictedValue(keyid=self.key, value="better")
        self.rv2.save()
        self.rv3 = RestrictedValue(keyid=self.key, value="best")
        self.rv3.save()

    ###########################################################################
    def tearDown(self):
        self.rv3.delete()
        self.rv2.delete()
        self.rv1.delete()
        self.key.delete()

    ###########################################################################
    def test_rvlist(self):
        """ Test rvlist with a key """
        response = self.client.get("/hostinfo/rvlist/rvlkey/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/restrval.template", "host/base.html"],
        )
        self.assertEqual(response.context["key"], "rvlkey")
        self.assertEqual(len(response.context["rvlist"]), 3)
        self.assertTrue(self.rv1 in response.context["rvlist"])
        self.assertTrue(self.rv2 in response.context["rvlist"])

    ###########################################################################
    def test_rvlist_wiki(self):
        """ Test rvlist in mediawiki format """
        response = self.client.get("/mediawiki/rvlist/rvlkey/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates], ["mediawiki/restrval.wiki"]
        )
        self.assertEqual(response.context["key"], "rvlkey")
        self.assertEqual(len(response.context["rvlist"]), 3)
        self.assertTrue(self.rv1 in response.context["rvlist"])
        self.assertTrue(self.rv2 in response.context["rvlist"])
        self.assertTrue(self.rv3 in response.context["rvlist"])


###############################################################################
class test_url_host_summary(TestCase):
    """ (r'^host_summary/(?P<hostname>.*)$', 'doHostSummary'),"""
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.host = Host(hostname="hosths")
        self.host.save()
        self.key = AllowedKey(key="hskey", validtype=2)
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host, keyid=self.key, value="kv1", origin="foo")
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host, keyid=self.key, value="kv2", origin="foo")
        self.kv2.save()
        self.al = HostAlias(hostid=self.host, alias="a1")
        self.al.save()
        self.link = Links(
            hostid=self.host, url="http://code.google.com/p/hostinfo", tag="hslink"
        )
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
        """ Test host summary with rvlsit """
        response = self.client.get("/hostinfo/host_summary/hosths")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/hostpage.template", "host/base.html"],
        )
        hostlist = response.context["hostlist"][0]
        self.assertEqual(hostlist["hostname"], "hosths")
        self.assertEqual(
            hostlist["links"],
            [
                '<a class="foreignlink" href="http://code.google.com/p/hostinfo">hslink</a>'
            ],
        )
        self.assertEqual(hostlist["hostview"], [("hskey", [self.kv1, self.kv2])])
        self.assertEqual(hostlist["aliases"], ["a1"])

    ###########################################################################
    def test_rvlist_wiki(self):
        """ Test host summary with rvlist in wiki format """
        response = self.client.get("/mediawiki/host_summary/hosths")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates], ["mediawiki/hostpage.wiki"]
        )
        hostlist = response.context["hostlist"][0]
        self.assertEqual(hostlist["hostname"], "hosths")
        self.assertEqual(
            hostlist["links"], ["[http://code.google.com/p/hostinfo hslink]"]
        )
        self.assertEqual(hostlist["hostview"], [("hskey", [self.kv1, self.kv2])])
        self.assertEqual(hostlist["aliases"], ["a1"])


###############################################################################
class test_url_host_create(TestCase):
    """ Create host creation """
    ###########################################################################
    def setUp(self):
        self.user = User.objects.create_user("fred", "fred@example.com", "secret")
        self.user.save()
        self.client = Client()
        self.client.login(username="fred", password="secret")

    ###########################################################################
    def test_create_choose(self):
        """ Choose the host to create """
        response = self.client.get("/hostinfo/hostcreate/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("host/hostcreate.template")

    ###########################################################################
    def test_create_choose_submit(self):
        """ Submit the choice """
        response = self.client.post(
            "/hostinfo/hostcreate/", {"newhost": "noob"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("host/hostcreate.template")
        self.assertIn(b"noob has been successfully created", response.content)
        host = Host.objects.filter(hostname="noob")
        self.assertEqual(len(host), 1)

    ###########################################################################
    def test_creation(self):
        """ Test the creation """
        response = self.client.post("/hostinfo/hostcreate/darwin/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("host/hostcreate.template")
        self.assertTemplateUsed("host/base.template")
        host = Host.objects.filter(hostname="darwin")
        self.assertEqual(len(host), 1)


###############################################################################
class test_url_host_edit(TestCase):
    """ Editing a host """
    ###########################################################################
    def setUp(self):
        clearAKcache()
        self.user = User.objects.create_user("fred", "fred@example.com", "secret")
        self.user.save()
        self.client = Client()
        self.client.login(username="fred", password="secret")
        self.host = Host(hostname="hosteh")
        self.host.save()
        self.key1 = AllowedKey(key="ehkey1", validtype=2)
        self.key1.save()
        self.key2 = AllowedKey(key="ehkey2", validtype=1)
        self.key2.save()
        self.kv1 = KeyValue(hostid=self.host, keyid=self.key1, value="oldval")
        self.kv1.save()
        self.key3 = AllowedKey(key="ehkey3", validtype=1, restrictedFlag=True)
        self.key3.save()
        self.rv1 = RestrictedValue(keyid=self.key3, value="true")
        self.rv1.save()
        self.rv2 = RestrictedValue(keyid=self.key3, value="false")
        self.rv2.save()
        self.kv2 = KeyValue(hostid=self.host, keyid=self.key3, value="false")
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
        """ Test selecting the host to edit """
        response = self.client.get("/hostinfo/hostedit/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            sorted(
                [
                    _.name
                    for _ in response.templates
                    if "django/forms" not in _.name
                ]
            ),
            sorted(["host/hostedit.template", "host/base.html"]),
        )

    ###########################################################################
    def test_hostpicked(self):
        """ We've picked a host - next"""
        response = self.client.post(
            "/hostinfo/hostedit/hosteh/", {"hostname": "hosteh"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/hostedit.template", "host/base.html", "host/hostediting.template"],
        )
        self.assertEqual(response.context["host"], "hosteh")
        self.assertEqual(response.context["editing"], True)
        self.assertEqual(
            response.context["kvlist"],
            [
                ("ehkey1", [self.kv1], "list", []),
                ("ehkey3", [self.kv2], "single", ["-Unknown-", "false", "true"]),
            ],
        )
        self.assertEqual(response.context["keylist"], [self.key2])

    ###########################################################################
    def test_hostedited(self):
        self.kv2.delete()
        response = self.client.post(
            "/hostinfo/hostedit/hosteh/",
            {
                "hostname": "hosteh",
                "_hostediting": "hosteh",
                "ehkey1.0": "newval",
                "_newkey.new": "ehkey3",
                "_newvalue.new": "true",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)

        self.kv2 = KeyValue.objects.filter(hostid=self.host, keyid=self.key3)
        self.assertEqual(self.kv2[0].value, "true")

        kv = KeyValue.objects.filter(hostid=self.host, keyid=self.key1)
        self.assertEqual(kv[0].value, "newval")


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
        self.host1 = Host(hostname="a_hosthl1")
        self.host1.save()
        self.link = Links(
            hostid=self.host1, url="http://code.google.com/p/hostinfo", tag="hslink"
        )
        self.link.save()
        self.host2 = Host(hostname="m_hosthl")
        self.host2.save()
        self.host3 = Host(hostname="z_hosthl2")
        self.host3.save()
        self.alias = HostAlias(hostid=self.host2, alias="alias")
        self.alias.save()
        self.key = AllowedKey(key="urlkey")
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host3, keyid=self.key, value="val")
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
        """Test that no criteria gets all hosts"""
        response = self.client.get("/hostinfo/hostlist/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/hostlist.template", "host/base.html"],
        )
        self.assertEqual(response.context["count"], 3)
        self.assertEqual(response.context["hostlist"][0]["hostname"], "a_hosthl1")
        self.assertEqual(response.context["hostlist"][1]["hostname"], "m_hosthl")
        self.assertEqual(response.context["hostlist"][2]["hostname"], "z_hosthl2")

    ###########################################################################
    def test_badkey(self):
        """ Ask for host list with bad criteria """
        response = self.client.get("/hostinfo/hostlist/badkey=foo/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted([t.name for t in response.templates]),
            ["host/base.html", "host/hostlist.template"],
        )
        self.assertEqual(
            response.context["error"].msg, "Must use an existing key, not badkey"
        )

    ###########################################################################
    def test_withcriteria(self):
        """ Ask for host list with criteria """
        response = self.client.get("/hostinfo/hostlist/urlkey=foo/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            sorted([t.name for t in response.templates]),
            ["host/base.html", "host/hostlist.template"],
        )

    ###########################################################################
    def test_withoptions(self):
        """ Ask for host list with options """
        response = self.client.get("/hostinfo/hostlist/urlkey=foo/dates")
        self.assertEqual(response.status_code, 301)
        response = self.client.get("/hostinfo/hostlist/urlkey=foo/dates", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            sorted([t.name for t in response.templates]),
            ["host/base.html", "host/hostlist.template"],
        )

    ###########################################################################
    def test_nohosts(self):
        """ Specify no hosts to get all hosts """
        response = self.client.get("/hostinfo/host/")
        self.assertTrue(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/hostlist.template", "host/base.html"],
        )
        self.assertEqual(response.context["count"], 3)
        self.assertEqual(response.context["hostlist"][0]["hostname"], "a_hosthl1")
        self.assertEqual(response.context["hostlist"][1]["hostname"], "m_hosthl")
        self.assertEqual(response.context["hostlist"][2]["hostname"], "z_hosthl2")

    ###########################################################################
    def test_hostcriteria(self):
        """ Test hostcriteria """
        response = self.client.get("/hostinfo/hostlist/z_hosthl2", follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/hostlist.template", "host/base.html"],
        )
        self.assertEqual(response.context["count"], 1)
        self.assertEqual(response.context["csvavailable"], "/hostinfo/csv/z_hosthl2")
        self.assertEqual(response.context["hostlist"][0]["hostname"], "z_hosthl2")

    ###########################################################################
    def test_multihostcriteria(self):
        """ Test multihostcriteria """
        response = self.client.get("/hostinfo/hostlist/urlkey.eq.val/")
        self.assertTrue(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        KeyValue.objects.filter(hostid=self.host2, keyid=self.key)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/hostlist.template", "host/base.html"],
        )
        self.assertEqual(response.context["title"], "urlkey.eq.val")
        self.assertEqual(response.context["count"], 1)
        self.assertEqual(response.context["hostlist"][0]["hostname"], "z_hosthl2")

    ###########################################################################
    def test_host_origin_option(self):
        """ Test origin """
        response = self.client.get("/hostinfo/hostlist/urlkey.ne.bar/opts=origin", follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/hostlist.template", "host/base.html"],
        )
        self.assertEqual(response.context["count"], 3)
        self.assertEqual(response.context["origin"], True)

    ###########################################################################
    def test_host_both_option(self):
        """ Test dates and origins """
        response = self.client.get("/hostinfo/hostlist/urlkey.ne.bar/opts=dates,origin")
        self.assertTrue(response.status_code, 200)
        self.assertTrue("error" not in response.context)
        self.assertEqual(
            [t.name for t in response.templates],
            ["host/hostlist.template", "host/base.html"],
        )
        self.assertEqual(response.context["count"], 3)
        self.assertEqual(response.context["origin"], True)
        self.assertEqual(response.context["dates"], True)


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
        self.host1 = Host(hostname="hostcsv1")
        self.host1.save()
        self.host2 = Host(hostname="hostcsv2")
        self.host2.save()
        self.key = AllowedKey(key="csvkey")
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host2, keyid=self.key, value="val")
        self.kv1.save()

    ###########################################################################
    def tearDown(self):
        self.kv1.delete()
        self.key.delete()
        self.host1.delete()
        self.host2.delete()

    ###########################################################################
    def test_csv(self):
        response = self.client.get("/hostinfo/csv/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertEqual(
            response["Content-Disposition"], "attachment; filename=allhosts.csv"
        )
        self.assertEqual(
            response.content, b"hostname,csvkey\r\nhostcsv1,\r\nhostcsv2,val\r\n"
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
        self.host1 = Host(hostname="hosthwt1")
        self.host1.save()
        self.link = Links(
            hostid=self.host1, url="http://code.google.com/p/hostinfo", tag="hslink"
        )
        self.link.save()
        self.host2 = Host(hostname="hosthwt2")
        self.host2.save()
        self.alias = HostAlias(hostid=self.host2, alias="alias")
        self.alias.save()
        self.key = AllowedKey(key="hwtkey")
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host2, keyid=self.key, value="val")
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
        """ Test a wiki table with query """
        response = self.client.get("/mediawiki/hosttable/hwtkey.ne.val/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(
            response.content,
            b"{| border=1\n|-\n!Hostname\n|-\n| [[Host:hosthwt1|hosthwt1]]\n|}\n",
        )

    ###########################################################################
    def test_wikitable_print(self):
        """ Test a wiki table but with selective printing """
        response = self.client.get(
            "/mediawiki/hosttable/hwtkey.def/print=hwtkey/order=hwtkey/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(
            response.content,
            b"{| border=1\n|-\n!Hostname\n!Hwtkey\n|-\n| [[Host:hosthwt2|hosthwt2]]\n| val\n|}\n",
        )


###############################################################################
class test_url_hostcmp(TestCase):
    """
    (r'^hostcmp/(?P<criteria>.*)/(?P<options>opts=.*)?$', 'doHostcmp'),
    """

    def setUp(self):
        clearAKcache()
        self.client = Client()
        self.host1 = Host(hostname="hostuhc1")
        self.host1.save()
        self.host2 = Host(hostname="hostuhc2")
        self.host2.save()
        self.key = AllowedKey(key="uhckey")
        self.key.save()
        self.kv1 = KeyValue(hostid=self.host1, keyid=self.key, value="val1")
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.host2, keyid=self.key, value="val2")
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
        response = self.client.get("/hostinfo/hostcmp/uhckey.def/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"<title> Comparison of host details uhckey.def</title>", response.content
        )
        self.assertIn(
            b'<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>',
            response.content,
        )
        self.assertIn(
            b'<a class="hostname" href="/hostinfo/host/hostuhc2">hostuhc2</a>',
            response.content,
        )
        self.assertIn(
            b'<a class="keyname" href="/hostinfo/keylist/uhckey">uhckey</a>',
            response.content,
        )
        self.assertIn(
            b'<a class="valuelink" href="/hostinfo/hostlist/uhckey.eq.val2">val2</a>',
            response.content,
        )
        self.assertEqual(
            set([t.name for t in response.templates]),
            set(["host/multihost.template", "host/base.html", "host/showall.template"]),
        )

    ###########################################################################
    def test_hostcmp_dates(self):
        response = self.client.get("/hostinfo/hostcmp/uhckey.def/opts=dates")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"<title> Comparison of host details uhckey.def</title>", response.content
        )
        self.assertIn(
            b'<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>',
            response.content,
        )
        self.assertIn(
            b"<input type=checkbox name=options value=dates  checked  >Show Dates",
            response.content,
        )
        self.assertIn(
            b"<input type=checkbox name=options value=origin  >Show Origin",
            response.content,
        )
        self.assertIn(b"Modified:", response.content)
        self.assertIn(b"Created:", response.content)
        self.assertEqual(
            set([t.name for t in response.templates]),
            set(["host/multihost.template", "host/base.html", "host/showall.template"]),
        )

    ###########################################################################
    def test_hostcmp_origin(self):
        response = self.client.get("/hostinfo/hostcmp/uhckey.def/opts=origin")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"<title> Comparison of host details uhckey.def</title>", response.content
        )
        self.assertIn(
            b'<a class="hostname" href="/hostinfo/host/hostuhc1">hostuhc1</a>',
            response.content,
        )
        self.assertIn(
            b"<input type=checkbox name=options value=origin  checked  >Show Origin",
            response.content,
        )
        self.assertIn(
            b"<input type=checkbox name=options value=dates  >Show Dates",
            response.content,
        )
        self.assertIn(b"Origin:", response.content)
        self.assertEqual(
            set([t.name for t in response.templates]),
            set(["host/multihost.template", "host/base.html", "host/showall.template"]),
        )


# EOF
