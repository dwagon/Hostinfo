""" Test hostinfo commands"""

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
import json
import os
import sys
import tempfile
import time

try:
    from StringIO import StringIO
except ImportError:  # pragma: no cover
    from io import StringIO

from host.models import Host, HostAlias, AllowedKey, RestrictedValue, Links
from host.models import HostinfoException, ReadonlyValueException
from host.models import RestrictedValueException
from host.models import addKeytoHost, run_from_cmdline
from host.models import clearAKcache, KeyValue


###############################################################################
class test_cmd_hostinfo_xml(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.h1 = Host(hostname="xh1", origin="me")
        self.h1.save()
        self.h2 = Host(hostname="xh2", origin="you")
        self.h2.save()
        self.ak1 = AllowedKey(key="xak1", numericFlag=True, desc="Test Key")
        self.ak1.save()
        self.ak2 = AllowedKey(key="xak2", restrictedFlag=True, desc="Restricted Test")
        self.ak2.save()
        self.rv = RestrictedValue(keyid=self.ak2, value="xkv3")
        self.rv.save()
        self.kv1 = KeyValue(hostid=self.h1, keyid=self.ak1, value="1", origin="foo")
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.h2, keyid=self.ak1, value="xkv2", origin="bar")
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.h1, keyid=self.ak2, value="xkv3", origin="baz")
        self.kv3.save()
        self.alias = HostAlias(hostid=self.h1, alias="xhalias")
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
        namespace = self.parser.parse_args(["--xml", "-p", "xak1"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn("<name>xak1</name>", output[0])
        self.assertIn("<desc>Test Key</desc>", output[0])
        self.assertIn("<numericFlag>True</numericFlag>", output[0])
        self.assertIn("<auditFlag>True</auditFlag>", output[0])
        self.assertIn("<type>single</type>", output[0])
        self.assertIn('<confitem key="xak1">1</confitem>', output[0])

    ###########################################################################
    def test_xml_restrictedkey(self):
        namespace = self.parser.parse_args(["--xml", "-p", "xak2"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn("<name>xak2</name>", output[0])
        self.assertIn("<desc>Restricted Test</desc>", output[0])
        self.assertIn("<numericFlag>False</numericFlag>", output[0])
        self.assertIn("<auditFlag>True</auditFlag>", output[0])
        self.assertIn("<restricted>", output[0])
        self.assertIn("<value>xkv3</value>", output[0])
        self.assertIn('<confitem key="xak2">xkv3</confitem>', output[0])

    ###########################################################################
    def test_hostinfo_xml(self):
        """Test outputting hosts only in xml mode"""
        namespace = self.parser.parse_args(["--xml"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn("<hostname>xh1</hostname>", output[0])
        self.assertIn("<hostname>xh2</hostname>", output[0])
        self.assertNotIn("confitem", output[0])
        # TODO: Replace with something that pulls the whole xml apart


###############################################################################
class test_cmd_hostinfo(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.h1 = Host(hostname="h1", origin="me")
        self.h1.save()
        self.h2 = Host(hostname="h2", origin="you")
        self.h2.save()
        self.ak1 = AllowedKey(key="ak1")
        self.ak1.save()
        self.ak2 = AllowedKey(key="ak2")
        self.ak2.save()
        self.kv1 = KeyValue(hostid=self.h1, keyid=self.ak1, value="kv1", origin="foo")
        self.kv1.save()
        self.kv2 = KeyValue(hostid=self.h2, keyid=self.ak1, value="kv2", origin="bar")
        self.kv2.save()
        self.kv3 = KeyValue(hostid=self.h1, keyid=self.ak2, value="kv3", origin="baz")
        self.kv3.save()
        self.alias = HostAlias(hostid=self.h1, alias="halias")
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
        hname = "good.lt.bad"
        th1 = Host(hostname=hname, origin="me")
        th1.save()
        namespace = self.parser.parse_args(["--host", hname])
        output = self.cmd.handle(namespace)
        self.assertIn(hname, output[0])
        self.assertEquals(output[1], 0)
        th1.delete()

    ###########################################################################
    def test_hostinfo(self):
        namespace = self.parser.parse_args([])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("h1\nh2\n", 0))

    ###########################################################################
    def testnomatches(self):
        namespace = self.parser.parse_args(["h3"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("", 1))

    ###########################################################################
    def testnormal_p(self):
        namespace = self.parser.parse_args(["-p", "ak1"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("h1\tak1=kv1\nh2\tak1=kv2\n", 0))

    ###########################################################################
    def testnormal_missingp(self):
        namespace = self.parser.parse_args(["-p", "ak1", "-p", "ak2"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("h1\tak1=kv1\tak2=kv3\nh2\tak1=kv2\tak2=\n", 0))

    ###########################################################################
    def testnormal_times(self):
        import time

        t = time.strftime("%Y-%m-%d", time.localtime())
        namespace = self.parser.parse_args(["-p", "ak1", "--times"])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output,
            (
                f"h1\t[Created: {t} Modified: {t}]\tak1=kv1[Created: {t}, Modified: {t}]\nh2\t[Created: {t} Modified: {t}]\tak1=kv2[Created: {t}, Modified: {t}]\n",
                0,
            ),
        )

    ###########################################################################
    def testnormal_origin(self):
        namespace = self.parser.parse_args(["-p", "ak1", "--origin"])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output,
            (
                "h1\t[Origin: me]\tak1=kv1[Origin: foo]\nh2\t[Origin: you]\tak1=kv2[Origin: bar]\n",
                0,
            ),
        )

    ###########################################################################
    def testbadkey(self):
        namespace = self.parser.parse_args(["-p", "badkey"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must use an existing key, not badkey")

    ###########################################################################
    def test_hostinfo_json(self):
        namespace = self.parser.parse_args(["--json"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        data = json.loads(output[0])
        self.assertTrue("h1" in data)
        self.assertTrue("h2" in data)

    ###########################################################################
    def test_hostinfo_jsonp(self):
        namespace = self.parser.parse_args(["--json", "-p", "ak1", "-p", "ak2"])
        output = self.cmd.handle(namespace)
        data = json.loads(output[0])
        self.assertEquals(data["h2"], {"ak1": ["kv2"]})

    ###########################################################################
    def test_hostinfo_csv(self):
        namespace = self.parser.parse_args(["--csv"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("hostname,\nh1\nh2", 0))

    ###########################################################################
    def test_hostinfo_csvp(self):
        namespace = self.parser.parse_args(["--csv", "-p", "ak1", "-p", "ak2"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('hostname,ak1,ak2\nh1,"kv1","kv3"\nh2,"kv2",', 0))

    ###########################################################################
    def test_hostinfo_csvsep(self):
        namespace = self.parser.parse_args(
            ["-p", "ak1", "-p", "ak2", "--csv", "--sep", "#"]
        )
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ('hostname#ak1#ak2\nh1#"kv1"#"kv3"\nh2#"kv2"#', 0))

    ###########################################################################
    def test_hostinfo_showall(self):
        namespace = self.parser.parse_args(["--showall"])
        output = self.cmd.handle(namespace)
        self.assertIn("ak1: kv1", output[0])
        self.assertIn("ak2: kv3", output[0])
        self.assertIn("ak1: kv2", output[0])

    ###########################################################################
    def test_hostinfo_count(self):
        namespace = self.parser.parse_args(["--count"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("2", 0))

    ###########################################################################
    def test_hostinfo_hostsep(self):
        namespace = self.parser.parse_args(["--hsep", ":"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("h1:h2\n", 0))

    ###########################################################################
    def test_hostinfo_xml_p(self):
        namespace = self.parser.parse_args(["--xml", "-p", "ak1"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn("<hostname>h1</hostname>", output[0])
        self.assertIn("<hostname>h2</hostname>", output[0])
        self.assertIn('<confitem key="ak1">kv1</confitem>', output[0])
        self.assertIn('<confitem key="ak1">kv2</confitem>', output[0])
        self.assertIn("<name>ak1</name>", output[0])
        self.assertIn("<type>single</type>", output[0])
        # TODO: Replace with something that pulls the whole xml apart

    ###########################################################################
    def test_hostinfo_xml_showall(self):
        namespace = self.parser.parse_args(["--xml", "--showall"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn("<name>ak1</name>", output[0])
        self.assertIn("<name>ak2</name>", output[0])
        self.assertIn('<confitem key="ak1">kv1</confitem>', output[0])
        self.assertIn('<confitem key="ak2">kv3</confitem>', output[0])
        # TODO: Replace with something that pulls the whole xml apart

    ###########################################################################
    def test_hostinfo_xml_aliases(self):
        namespace = self.parser.parse_args(["--xml", "--aliases", "--showall"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)
        self.assertIn("<alias>halias</alias>", output[0])
        self.assertIn("<name>ak1</name>", output[0])
        self.assertIn("<name>ak2</name>", output[0])
        self.assertIn('<confitem key="ak1">kv1</confitem>', output[0])
        self.assertIn('<confitem key="ak2">kv3</confitem>', output[0])
        # TODO: Replace with something that pulls the whole xml apart

    ###########################################################################
    def test_hostinfo_valuereport(self):
        namespace = self.parser.parse_args(["--valuereport", "ak1"])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output[0],
            "ak1 set: 2 100.00%\nak1 unset: 0 0.00%\n\nkv1 1 50.00%\nkv2 1 50.00%\n",
        )
        self.assertEquals(output[1], 0)

        # No matches
        namespace = self.parser.parse_args(["--valuereport", "ak1", "ak2=novalue"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[0], "")
        self.assertEquals(output[1], 1)

    ###########################################################################
    def test_hostinfo_valuereport_badkey(self):
        """Make sure the key exists for a valuereport - Iss06"""
        namespace = self.parser.parse_args(["--valuereport", "badkey"])
        with self.assertRaises(HostinfoException):
            self.cmd.handle(namespace)


###############################################################################
class test_cmd_addalias(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_addalias import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_hostnotexists(self):
        """Test creating an alias of a host that doesn't exist"""
        namespace = self.parser.parse_args(["host", "alias"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host host doesn't exist")

    ###########################################################################
    def test_aliasexists(self):
        """Test creating an alias that already exists"""
        host = Host(hostname="host")
        host.save()
        alias = Host(hostname="alias")
        alias.save()
        namespace = self.parser.parse_args(["host", "alias"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host alias already exists")
        host.delete()
        alias.delete()

    ###########################################################################
    def test_alias_of_alias(self):
        """Can we create an alias to an alias"""
        host = Host(hostname="aoahost")
        host.save()
        alias = HostAlias(hostid=host, alias="oldalias")
        alias.save()
        namespace = self.parser.parse_args(["oldalias", "newalias"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        newalias = HostAlias.objects.get(alias="newalias")
        self.assertEquals(newalias.hostid, host)
        newaliases = HostAlias.objects.filter(hostid=host)
        self.assertEquals(len(newaliases), 2)
        for a in newaliases:
            a.delete()
        host.delete()

    ###########################################################################
    def test_creation(self):
        """Make sure than an alias is created"""
        host = Host(hostname="host")
        host.save()
        namespace = self.parser.parse_args(["--origin", "test", "host", "alias"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        alias = HostAlias.objects.get(hostid=host)
        self.assertEquals(alias.origin, "test")
        self.assertEquals(alias.alias, "alias")
        alias.delete()
        host.delete()


###############################################################################
class test_cmd_addhost(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_addhost import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_alreadyexists(self):
        host = Host(hostname="host")
        host.save()
        namespace = self.parser.parse_args(["host"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host host already exists")
        host.delete()
        h = Host.objects.all()
        self.assertEquals(len(h), 0)

    ###########################################################################
    def test_creation(self):
        namespace = self.parser.parse_args(["--origin", "test", "host"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        host = Host.objects.get(hostname="host")
        self.assertEquals(host.hostname, "host")
        self.assertEquals(host.origin, "test")
        host.delete()

    ###########################################################################
    def test_lowercase(self):
        namespace = self.parser.parse_args(["HOST"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        host = Host.objects.get(hostname="host")
        self.assertEquals(host.hostname, "host")
        host.delete()

    ###########################################################################
    def test_badname(self):
        namespace = self.parser.parse_args(["--", "-badhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg,
            "Host begins with a forbidden character ('-') - not adding",
        )
        h = Host.objects.all()
        self.assertEquals(len(h), 0)


###############################################################################
class test_cmd_deletelink(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_deletelink import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname="linkhost")
        self.host.save()
        self.link = Links(hostid=self.host, tag="home", url="http://dwagon.net")
        self.link.save()

    ###########################################################################
    def tearDown(self):
        self.link.delete()
        self.host.delete()

    ###########################################################################
    def test_deleteelink(self):
        namespace = self.parser.parse_args(["--tag", "home", "linkhost"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        lnk = Links.objects.filter(hostid=self.host)
        self.assertEquals(len(lnk), 0)

    ###########################################################################
    def test_badhost(self):
        namespace = self.parser.parse_args(["--tag", "home", "badhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host badhost doesn't exist")

    ###########################################################################
    def test_everytag(self):
        namespace = self.parser.parse_args(["--everytag", "linkhost"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        lnk = Links.objects.filter(hostid=self.host)
        self.assertEquals(len(lnk), 0)


###############################################################################
class test_cmd_addlink(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_addlink import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname="linkhost")
        self.host.save()

    ###########################################################################
    def tearDown(self):
        self.host.delete()

    ###########################################################################
    def test_createlink(self):
        namespace = self.parser.parse_args(["home", "http://dwagon.net", "linkhost"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        lnk = Links.objects.get(hostid=self.host)
        self.assertEquals(lnk.url, "http://dwagon.net")
        self.assertEquals(lnk.tag, "home")

    ###########################################################################
    def test_badhost(self):
        namespace = self.parser.parse_args(["home", "http://dwagon.net", "badhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host badhost doesn't exist")

    ###########################################################################
    def test_duplicatetag(self):
        orig = Links(hostid=self.host, tag="home", url="http://dwagon.net")
        orig.save()
        namespace = self.parser.parse_args(["home", "http://dwagon.net", "linkhost"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, ("Host linkhost already has a link with tag home", 1))
        orig.delete()

    ###########################################################################
    def test_update(self):
        orig = Links(hostid=self.host, tag="home", url="http://google.com")
        orig.save()
        namespace = self.parser.parse_args(
            ["--update", "home", "http://dwagon.net", "linkhost"]
        )
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        lnk = Links.objects.get(hostid=self.host)
        self.assertEquals(lnk.url, "http://dwagon.net")


###############################################################################
class test_cmd_addkey(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_addkey import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_alreadyExists(self):
        ak = AllowedKey(key="key_addkey_t1")
        ak.save()
        namespace = self.parser.parse_args(["key_addkey_t1"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg, "Key already exists with that name: key_addkey_t1"
        )
        ak.delete()

    ###########################################################################
    def test_addRestricted(self):
        namespace = self.parser.parse_args(["--restricted", "key_addkey_t2"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t2")
        self.assertEquals(key.restrictedFlag, True)
        self.assertEquals(key.readonlyFlag, False)
        self.assertEquals(key.auditFlag, True)
        self.assertEquals(key.get_validtype_display(), "single")
        self.assertEquals(key.desc, "")
        key.delete()

    ###########################################################################
    def test_addReadonly(self):
        namespace = self.parser.parse_args(["--readonly", "key_addkey_t3"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t3")
        self.assertEquals(key.restrictedFlag, False)
        self.assertEquals(key.readonlyFlag, True)
        self.assertEquals(key.auditFlag, True)
        key.delete()

    ###########################################################################
    def test_addSingle(self):
        namespace = self.parser.parse_args(["key_addkey_t4", "single"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t4")
        self.assertEquals(key.auditFlag, True)
        self.assertEquals(key.get_validtype_display(), "single")
        key.delete()

    ###########################################################################
    def test_addList(self):
        namespace = self.parser.parse_args(["key_addkey_t5", "list"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t5")
        self.assertEquals(key.get_validtype_display(), "list")
        key.delete()

    ###########################################################################
    def test_addDate(self):
        namespace = self.parser.parse_args(["key_addkey_t6", "date"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t6")
        self.assertEquals(key.get_validtype_display(), "date")
        key.delete()

    ###########################################################################
    def test_withDescription(self):
        namespace = self.parser.parse_args(
            ["key_addkey_t7", "single", "this", "is", "a", "description"]
        )
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t7")
        self.assertEquals(key.desc, "this is a description")
        key.delete()

    ###########################################################################
    def test_withExplicitKeyType(self):
        namespace = self.parser.parse_args(["--keytype", "list", "key_addkey_t8"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t8")
        key.delete()

    ###########################################################################
    def test_withExplicitKeyTypeAndDesc(self):
        namespace = self.parser.parse_args(
            ["--keytype", "date", "key_addkey_t9", "this", "is", "a", "description"]
        )
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t9")
        self.assertEquals(key.get_validtype_display(), "date")
        key.delete()

    ###########################################################################
    def test_lowercase(self):
        namespace = self.parser.parse_args(["KEY_ADDKEY_T10"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t10")
        key.delete()

    ###########################################################################
    def test_addnoaudit(self):
        namespace = self.parser.parse_args(["--noaudit", "key_addkey_t11"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        key = AllowedKey.objects.get(key="key_addkey_t11")
        self.assertEquals(key.auditFlag, False)
        key.delete()

    ###########################################################################
    def test_unknowntype(self):
        namespace = self.parser.parse_args(["key_addkey_t12", "invalid", "description"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg, "Unknown type invalid - should be one of single,list,date"
        )


###############################################################################
class test_cmd_addrestrictedvalue(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_addrestrictedvalue import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.key = AllowedKey(key="restr", validtype=1, restrictedFlag=True)
        self.key.save()

    ###########################################################################
    def tearDown(self):
        self.key.delete()

    ###########################################################################
    def test_addvalue(self):
        namespace = self.parser.parse_args(["restr=value"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        rv = RestrictedValue.objects.filter()[0]
        self.assertEquals(rv.value, "value")
        self.assertEquals(rv.keyid, self.key)

    ###########################################################################
    def test_missingkey(self):
        namespace = self.parser.parse_args(["key2=value"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No key key2 found")

    ###########################################################################
    def test_unrestricted(self):
        self.key2 = AllowedKey(key="unrestr", validtype=1, restrictedFlag=False)
        self.key2.save()
        namespace = self.parser.parse_args(["unrestr=value"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Key unrestr isn't a restrictedvalue key")
        self.key2.delete()

    ###########################################################################
    def test_alreadyexists(self):
        self.rv = RestrictedValue(keyid=self.key, value="value")
        self.rv.save()
        namespace = self.parser.parse_args(["restr=value"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg, "Already a key restr=value in the restrictedvalue list"
        )
        self.rv.delete()

    ###########################################################################
    def test_wrongformat(self):
        namespace = self.parser.parse_args(["key value"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must be specified in key=value format")


###############################################################################
class test_cmd_addvalue(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_addvalue import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname="testhost")
        self.host.save()

    ###########################################################################
    def tearDown(self):
        self.host.delete()

    ###########################################################################
    def test_addvalue(self):
        """Test normal operation of adding a new key/value pair"""
        key = AllowedKey(key="key_addvalue_t1", validtype=1)
        key.save()
        namespace = self.parser.parse_args(
            ["--origin", "whence", "key_addvalue_t1=VALUE", "testhost"]
        )
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        kv = KeyValue.objects.filter()[0]
        self.assertEquals(kv.hostid, self.host)
        self.assertEquals(kv.value, "value")
        self.assertEquals(kv.origin, "whence")
        key.delete()

    ###########################################################################
    def test_multiplehosts(self):
        key = AllowedKey(key="key_addvalue_t2", validtype=1)
        key.save()
        host2 = Host(hostname="testhost2")
        host2.save()
        namespace = self.parser.parse_args(
            ["--origin", "whence2", "key_addvalue_t2=value2", "testhost", "testhost2"]
        )
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        for h in (self.host, host2):
            kv = KeyValue.objects.filter(hostid=h)[0]
            self.assertEquals(kv.value, "value2")
            self.assertEquals(kv.origin, "whence2")
        key.delete()
        host2.delete()

    ###########################################################################
    def test_restrictedkey(self):
        """Test that we can't add a non-allowed value to a restricted key
        Then test that we can add an allowed value to a restricted key
        """
        key = AllowedKey(key="rkey", validtype=1, restrictedFlag=True)
        key.save()
        rv = RestrictedValue(keyid=key, value="restrvalue")
        rv.save()

        namespace = self.parser.parse_args(["rkey=value", "testhost"])
        with self.assertRaises(RestrictedValueException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Cannot add rkey=value to a restricted key")
        kv = KeyValue.objects.filter(keyid=key)
        self.assertEquals(len(kv), 0)

        namespace = self.parser.parse_args(["rkey=restrvalue", "testhost"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        kv = KeyValue.objects.get(keyid=key)
        self.assertEquals(kv.value, "restrvalue")

        rv.delete()
        key.delete()

    ###########################################################################
    def test_baddsyntax(self):
        """Test that we can't add something that doesn't match key=value"""
        namespace = self.parser.parse_args(["badvalue", "testhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must be specified in key=value format")

    ###########################################################################
    def test_readonlykey(self):
        """Test that we can't add a value to a readonly key without the correct option"""
        key = AllowedKey(key="rokey", validtype=1, readonlyFlag=True)
        key.save()
        namespace = self.parser.parse_args(["rokey=value", "testhost"])
        with self.assertRaises(ReadonlyValueException):
            self.cmd.handle(namespace)
        kv = KeyValue.objects.filter(keyid=key)
        self.assertEqual(list(kv), [])

        # Now try with correct options
        namespace = self.parser.parse_args(
            ["--readonlyupdate", "rokey=value", "testhost"]
        )
        self.cmd.handle(namespace)
        kv = KeyValue.objects.filter(keyid=key)
        self.assertEqual(kv[0].value, "value")
        key.delete()

    ###########################################################################
    def test_whitespacevalue(self):
        """Confirm that values are stripped before adding - Iss02"""
        key = AllowedKey(key="key_addvalue_t1", validtype=1)
        key.save()
        namespace = self.parser.parse_args(["key_addvalue_t1= VALUE", "testhost"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        kv = KeyValue.objects.filter()[0]
        self.assertEquals(kv.hostid, self.host)
        self.assertEquals(kv.value, "value")
        key.delete()

    ###########################################################################
    def test_missingkey(self):
        namespace = self.parser.parse_args(["mkey=value", "testhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must use an existing key, not mkey")


###############################################################################
class test_cmd_deletealias(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_deletealias import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname="host")
        self.host.save()

    ###########################################################################
    def tearDown(self):
        self.host.delete()

    ###########################################################################
    def test_deletealias(self):
        """Test deletion of an alias"""
        alias = HostAlias(hostid=self.host, alias="alias")
        alias.save()
        namespace = self.parser.parse_args(["alias"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        alias.delete()
        aliaslist = HostAlias.objects.all()
        self.assertEquals(len(aliaslist), 0)

    ###########################################################################
    def test_deletemissingalias(self):
        """Test the attempted deletion of an alias that doesn't exist"""
        namespace = self.parser.parse_args(["badalias"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No alias called badalias")


###############################################################################
class test_cmd_deletehost(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_deletehost import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_nonlethal(self):
        """Test that without --lethal it does nothing"""
        h = Host(hostname="test")
        h.save()
        namespace = self.parser.parse_args(["test"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Didn't do delete as no --lethal specified")
        hosts = Host.objects.all()
        self.assertEqual(len(hosts), 1)
        h.delete()

    ###########################################################################
    def test_deleterefers(self):
        """Test that aliases and kv pairs get deleted as well"""
        h = Host(hostname="test")
        h.save()
        a = HostAlias(hostid=h, alias="testalias")
        a.save()
        ak = AllowedKey(key="key_deletehost", validtype=1)
        ak.save()
        kv = KeyValue(hostid=h, keyid=ak, value="foo")
        kv.save()

        namespace = self.parser.parse_args(["--lethal", "test"])
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
        """Test the deletion of a host"""
        h = Host(hostname="test")
        h.save()
        namespace = self.parser.parse_args(["--lethal", "test"])
        retval = self.cmd.handle(namespace)
        self.assertEquals(retval, (None, 0))
        hosts = Host.objects.all()
        self.assertEqual(len(hosts), 0)
        h.delete()

    ###########################################################################
    def test_deletewronghost(self):
        """Test the deletion of a host that doesn't exist"""
        namespace = self.parser.parse_args(["--lethal", "test2"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host test2 doesn't exist")


###############################################################################
class test_cmd_deleterestrictedvalue(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_deleterestrictedvalue import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

        self.key = AllowedKey(key="restr", validtype=1, restrictedFlag=True)
        self.key.save()
        self.rv = RestrictedValue(keyid=self.key, value="allowed")
        self.rv.save()

    ###########################################################################
    def tearDown(self):
        self.rv.delete()
        self.key.delete()

    ###########################################################################
    def test_deleterestrval(self):
        """Test the deletion of a restricted value"""
        namespace = self.parser.parse_args(["restr=allowed"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        rv = RestrictedValue.objects.all()
        self.assertEquals(len(rv), 0)

    ###########################################################################
    def test_missingvalue(self):
        """Test the deletion of a value that doesn't exist"""
        namespace = self.parser.parse_args(["restr=bad"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg, "No key restr=bad in the restrictedvalue list"
        )

    ###########################################################################
    def test_badkeyname(self):
        """Test the deletion from a key that doesn't exist"""
        namespace = self.parser.parse_args(["bad=allowed"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg, "No key bad=allowed in the restrictedvalue list"
        )

    ###########################################################################
    def test_badkeytype(self):
        """Test the deletion of a value from a non-restricted key"""
        k1 = AllowedKey(key="free", validtype=1, restrictedFlag=False)
        k1.save()
        namespace = self.parser.parse_args(["free=allowed"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg, "No key free=allowed in the restrictedvalue list"
        )
        k1.delete()

    ###########################################################################
    def test_badformat(self):
        """Test specifying the args badly"""
        namespace = self.parser.parse_args(["foobar"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must be specified in key=value format")


###############################################################################
class test_cmd_deletevalue(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_deletevalue import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.h1 = Host(hostname="host_delval")
        self.h1.save()
        self.ak = AllowedKey(key="key_dv")
        self.ak.save()
        self.kv = KeyValue(hostid=self.h1, keyid=self.ak, value="deletevalue")
        self.kv.save()

    ###########################################################################
    def tearDown(self):
        self.kv.delete()
        self.ak.delete()
        self.h1.delete()

    ###########################################################################
    def test_deletevalue(self):
        """Test the deletion of a value"""
        namespace = self.parser.parse_args(["key_dv=deletevalue", "host_delval"])
        output = self.cmd.handle(namespace)
        kvlist = KeyValue.objects.filter(hostid=self.h1)
        self.assertEquals(output, (None, 0))
        self.assertEquals(len(kvlist), 0)

    ###########################################################################
    def test_delete_novalue(self):
        """Test the deletion of a value where the value isn't specified"""
        namespace = self.parser.parse_args(["key_dv", "host_delval"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kvlist = KeyValue.objects.filter(hostid=self.h1)
        self.assertEquals(len(kvlist), 0)

    ###########################################################################
    def test_badhost(self):
        """Test deleting from a host that doesn't exists"""
        namespace = self.parser.parse_args(["key_dv=deletevalue", "badhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Unknown host: badhost")
        kvlist = KeyValue.objects.filter(hostid=self.h1)
        self.assertEquals(len(kvlist), 1)

    ###########################################################################
    def test_readonlydeletion(self):
        """Test deleting a readonly value"""
        """ Test deleting a value from a host that doesn't have it"""
        ak2 = AllowedKey(key="key2_dv", readonlyFlag=True)
        ak2.save()
        kv2 = KeyValue(hostid=self.h1, keyid=ak2, value="deletevalue")
        kv2.save(readonlychange=True)
        namespace = self.parser.parse_args(["key2_dv=deletevalue", "host_delval"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Cannot delete a readonly value")
        kv2.delete(readonlychange=True)
        ak2.delete()

    ###########################################################################
    def test_badkey(self):
        """Test deleting a value from a key that doesn't exist"""
        namespace = self.parser.parse_args(["badkey_dv=deletevalue", "host_delval"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must use an existing key, not badkey_dv")

    ###########################################################################
    def test_deletebadkey(self):
        """Test deleting a value from a host that doesn't have it"""
        ak = AllowedKey(key="key3_dv")
        ak.save()
        namespace = self.parser.parse_args(["key3_dv=deletevalue", "host_delval"])
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
        from host.commands.cmd_hostinfo_history import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.t = time.strftime("%Y-%m-%d", time.localtime())

    ###########################################################################
    def test_badhost(self):
        namespace = self.parser.parse_args(["badhost"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("", 1))

    ###########################################################################
    def test_origin(self):
        host = Host(hostname="host_history_o")
        host.save()
        ak = AllowedKey(key="key4_dv")
        ak.save()
        kv = KeyValue(keyid=ak, hostid=host, value="historic", origin="kv_origin")
        kv.save()
        namespace = self.parser.parse_args(["-o", "host_history_o"])
        output = self.cmd.handle(namespace)
        self.assertTrue("kv_origin" in output[0])
        self.assertTrue(self.t in output[0])
        kv.delete()
        ak.delete()
        host.delete()

    ###########################################################################
    def test_hostadd(self):
        host = Host(hostname="host_history_ha")
        host.save()
        namespace = self.parser.parse_args(["host_history_ha"])
        output = self.cmd.handle(namespace)
        self.assertTrue("Host:host_history_ha added" in output[0])
        self.assertTrue(self.t in output[0])
        host.delete()

    ###########################################################################
    def test_valadd(self):
        host = Host(hostname="host_history_va")
        host.save()
        ak = AllowedKey(key="key3_dv")
        ak.save()
        kv = KeyValue(keyid=ak, hostid=host, value="historic")
        kv.save()
        namespace = self.parser.parse_args(["host_history_va"])
        output = self.cmd.handle(namespace)
        self.assertTrue("added host_history_va:key3_dv=historic" in output[0])
        self.assertTrue(self.t in output[0])
        kv.delete()
        ak.delete()
        host.delete()

    ###########################################################################
    def test_valdelete(self):
        host = Host(hostname="host_history_vd")
        host.save()
        ak = AllowedKey(key="key4_dv")
        ak.save()
        kv = KeyValue(keyid=ak, hostid=host, value="historic")
        kv.save()
        kv.delete()
        namespace = self.parser.parse_args(["host_history_vd"])
        output = self.cmd.handle(namespace)
        self.assertTrue("deleted host_history_vd:key4_dv=historic" in output[0])
        self.assertTrue(self.t in output[0])
        ak.delete()
        host.delete()


###############################################################################
class test_cmd_import(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_import import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def tearDown(self):
        pass

    ###########################################################################
    def test_badfile(self):
        namespace = self.parser.parse_args(["badfile"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "File badfile doesn't exist")

    ###########################################################################
    def test_basic_import(self):
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(
            b"""
        <hostinfo> <key> <name>importkey</name> <type>single</type>
        <readonlyFlag>False</readonlyFlag> <auditFlag>False</auditFlag>
        <docpage>None</docpage> <desc>Testing import key</desc> </key>
        <host docpage="None" > <hostname>importhost</hostname>
        <data> <confitem key="importkey">4</confitem> </data> </host> </hostinfo>"""
        )
        tmpf.close()
        namespace = self.parser.parse_args([tmpf.name])
        self.cmd.handle(namespace)
        try:
            os.unlink(tmpf.name)
        except OSError:  # pragma: no cover
            pass
        host = Host.objects.get(hostname="importhost")
        key = AllowedKey.objects.get(key="importkey")
        self.assertEquals(key.desc, "Testing import key")
        self.assertEquals(key.readonlyFlag, False)
        self.assertEquals(key.auditFlag, False)
        keyval = KeyValue.objects.get(hostid=host, keyid=key)
        self.assertEquals(keyval.value, "4")

    ###########################################################################
    def test_list_import(self):
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(
            b"""<hostinfo> <key> <name>importlistkey</name> <type>list</type>
        <readonlyFlag>True</readonlyFlag> <auditFlag>True</auditFlag>
        <docpage>None</docpage> <desc>Listkey</desc> </key> <host docpage="None" >
        <hostname>importhost2</hostname> <data>
        <confitem key="importlistkey">foo</confitem>
        <confitem key="importlistkey">bar</confitem> </data> </host> </hostinfo>"""
        )
        tmpf.close()
        namespace = self.parser.parse_args([tmpf.name])
        self.cmd.handle(namespace)
        try:
            os.unlink(tmpf.name)
        except OSError:  # pragma: no cover
            pass
        host = Host.objects.get(hostname="importhost2")
        key = AllowedKey.objects.get(key="importlistkey")
        self.assertEquals(key.readonlyFlag, True)
        self.assertEquals(key.auditFlag, True)
        keyvals = KeyValue.objects.filter(hostid=host, keyid=key)
        self.assertEquals(len(keyvals), 2)
        vals = sorted([kv.value for kv in keyvals])
        self.assertEquals(["bar", "foo"], vals)

    ###########################################################################
    def test_restricted_import(self):
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(
            b"""<hostinfo><key><name>importrestkey</name>
        <type>single</type> <readonlyFlag>False</readonlyFlag>
        <auditFlag>True</auditFlag> <docpage></docpage> <desc>Operating System</desc>
        <restricted> <value>alpha</value> <value>beta</value> </restricted> </key>
        <host docpage="None" > <hostname>importhost3</hostname> <data>
        <confitem key="importrestkey">alpha</confitem> </data> </host> </hostinfo>"""
        )
        tmpf.close()
        namespace = self.parser.parse_args([tmpf.name])
        self.cmd.handle(namespace)
        try:
            os.unlink(tmpf.name)
        except OSError:  # pragma: no cover
            pass
        host = Host.objects.get(hostname="importhost3")
        key = AllowedKey.objects.get(key="importrestkey")
        self.assertEquals(key.readonlyFlag, False)
        self.assertEquals(key.auditFlag, True)
        keyvals = KeyValue.objects.get(hostid=host, keyid=key)
        self.assertEquals(keyvals.value, "alpha")

    ###########################################################################
    def test_change_existingkey(self):
        key = AllowedKey(
            key="importexisting",
            validtype=1,
            readonlyFlag=True,
            restrictedFlag=False,
            auditFlag=False,
            desc="old desc",
        )
        key.save()
        tmpf = tempfile.NamedTemporaryFile(delete=False)
        tmpf.write(
            b"""<hostinfo><key><name>importexisting</name>
        <type>single</type> <readonlyFlag>False</readonlyFlag>
        <auditFlag>True</auditFlag> <docpage></docpage> <desc>New Desc</desc>
        <restricted> <value>alpha</value> <value>beta</value> </restricted> </key>
        <host docpage="None" > <hostname>importhost4</hostname> <data>
        <confitem key="importexisting">alpha</confitem> </data> </host> </hostinfo>"""
        )
        tmpf.close()
        namespace = self.parser.parse_args([tmpf.name])
        self.cmd.handle(namespace)
        try:
            os.unlink(tmpf.name)
        except OSError:  # pragma: no cover
            pass
        host = Host.objects.get(hostname="importhost4")
        newkey = AllowedKey.objects.get(key="importexisting")
        self.assertEquals(newkey.readonlyFlag, False)
        self.assertEquals(newkey.auditFlag, True)
        self.assertEquals(newkey.desc, "New Desc")
        keyvals = KeyValue.objects.get(hostid=host, keyid=newkey)
        self.assertEquals(keyvals.value, "alpha")
        key.delete()
        newkey.delete()


###############################################################################
class test_cmd_listalias(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_listalias import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname="host")
        self.host.save()
        self.alias1 = HostAlias(hostid=self.host, alias="foo")
        self.alias1.save()
        self.alias2 = HostAlias(hostid=self.host, alias="bar")
        self.alias2.save()

    ###########################################################################
    def tearDown(self):
        self.alias1.delete()
        self.alias2.delete()
        self.host.delete()

    ###########################################################################
    def test_listhost(self):
        """Test listing the aliases of a host"""
        namespace = self.parser.parse_args(["host"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("host\nbar\nfoo\n", 0))

    ###########################################################################
    def test_listnoaliases(self):
        """Test list aliases where there are none"""
        h = Host(hostname="test2")
        h.save()
        namespace = self.parser.parse_args(["test2"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("test2\n", 1))
        h.delete()

    ###########################################################################
    def test_listbadhost(self):
        """Test list aliases of a host that doesn't exist"""
        namespace = self.parser.parse_args(["badhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Host badhost doesn't exist")

    ###########################################################################
    def test_listall(self):
        """Test listing all aliases"""
        namespace = self.parser.parse_args(["--all"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("bar host\nfoo host\n", 0))

    ###########################################################################
    def test_listnone(self):
        """Test listing neither all or a host"""
        namespace = self.parser.parse_args([])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("bar host\nfoo host\n", 0))


###############################################################################
class test_cmd_listrestrictedvalue(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_listrestrictedvalue import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.key = AllowedKey(key="restr", validtype=1, restrictedFlag=True)
        self.key.save()
        self.rv = RestrictedValue(keyid=self.key, value="allowed")
        self.rv.save()

    ###########################################################################
    def tearDown(self):
        self.rv.delete()
        self.key.delete()

    ###########################################################################
    def test_list(self):
        """Test normal behaviour"""
        namespace = self.parser.parse_args(["restr"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("allowed\n", 0))

    ###########################################################################
    def test_badkey(self):
        """Specfied key doesn't exist"""
        namespace = self.parser.parse_args(["nokey"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No key nokey found")


###############################################################################
class test_cmd_mergehost(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_mergehost import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host1 = Host(hostname="mrghost1")
        self.host1.save()
        self.host2 = Host(hostname="mrghost2")
        self.host2.save()
        self.key1 = AllowedKey(key="mergesingle", validtype=1)
        self.key1.save()
        self.key2 = AllowedKey(key="mergelist", validtype=2)
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
        namespace = self.parser.parse_args(["--src", "mrghost1", "--dst", "mrghost2"])
        kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value="val1")
        kv1.save()
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key1)
        self.assertEqual(kv[0].value, "val1")

    ###########################################################################
    def test_mergehost_list(self):
        """Merge two hosts with overlapping lists"""
        namespace = self.parser.parse_args(["--src", "mrghost1", "--dst", "mrghost2"])
        addKeytoHost(host="mrghost1", key="mergelist", value="a")
        addKeytoHost(host="mrghost1", key="mergelist", value="b", appendFlag=True)
        addKeytoHost(host="mrghost1", key="mergelist", value="c", appendFlag=True)
        addKeytoHost(host="mrghost2", key="mergelist", value="c")
        addKeytoHost(host="mrghost2", key="mergelist", value="d", appendFlag=True)
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key2)
        vals = sorted([k.value for k in kv])
        self.assertEqual(vals, ["a", "b", "c", "d"])

    ###########################################################################
    def test_merge_collide(self):
        """Merge two hosts that have the same key set with a different value"""
        namespace = self.parser.parse_args(["--src", "mrghost1", "--dst", "mrghost2"])
        kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value="val1")
        kv1.save()
        kv2 = KeyValue(hostid=self.host2, keyid=self.key1, value="val2")
        kv2.save()
        output = self.cmd.handle(namespace)
        errout = sys.stderr.getvalue()
        errmsgs = [
            "Collision: mergesingle src=val1 dst=val2",
            "To keep dst mrghost2 value val2: hostinfo_addvalue --update mergesingle='val2' mrghost1",
            "To keep src mrghost1 value val1: hostinfo_addvalue --update mergesingle='val1' mrghost2",
        ]
        for msg in errmsgs:
            self.assertIn(msg, errout)
        self.assertEquals(output, ("Failed to merge", 1))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key1)
        self.assertEqual(kv[0].value, "val2")

    ###########################################################################
    def test_merge_collide_force(self):
        """Force merge two hosts that have the same key set with a different value"""
        namespace = self.parser.parse_args(
            ["--force", "--src", "mrghost1", "--dst", "mrghost2"]
        )
        kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value="val1")
        kv1.save()
        kv2 = KeyValue(hostid=self.host2, keyid=self.key1, value="val2")
        kv2.save()
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key1)
        self.assertEqual(kv[0].value, "val2")

    ###########################################################################
    def test_merge_no_collide(self):
        """Merge two hosts that have the same key set with the same value"""
        namespace = self.parser.parse_args(["--src", "mrghost1", "--dst", "mrghost2"])
        kv1 = KeyValue(hostid=self.host1, keyid=self.key1, value="vala")
        kv1.save()
        kv2 = KeyValue(hostid=self.host2, keyid=self.key1, value="vala")
        kv2.save()
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host2.id, keyid=self.key1)
        self.assertEqual(kv[0].value, "vala")

    ###########################################################################
    def test_merge_no_srchost(self):
        """Attempt merge where srchost doesn't exist"""
        namespace = self.parser.parse_args(["--src", "badhost", "--dst", "mrghost2"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Source host badhost doesn't exist")

    ###########################################################################
    def test_merge_no_dsthost(self):
        """Attempt merge where dsthost doesn't exist"""
        namespace = self.parser.parse_args(["--src", "mrghost1", "--dst", "badhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Destination host badhost doesn't exist")


###############################################################################
class test_cmd_renamehost(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_renamehost import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.host = Host(hostname="renhost")
        self.host.save()
        self.host2 = Host(hostname="renhost2")
        self.host2.save()

    ###########################################################################
    def tearDown(self):
        self.host.delete()
        self.host2.delete()

    ###########################################################################
    def test_renamehost(self):
        namespace = self.parser.parse_args(["--src", "renhost", "--dst", "newhost"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        hosts = Host.objects.filter(hostname="newhost")
        self.assertEquals(hosts[0], self.host)
        hosts = Host.objects.filter(hostname="renhost")
        self.assertEquals(len(hosts), 0)

    ###########################################################################
    def test_renamehbadost(self):
        namespace = self.parser.parse_args(["--src", "renbadhost", "--dst", "newhost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "There is no host called renbadhost")

    ###########################################################################
    def test_renameexisting(self):
        namespace = self.parser.parse_args(["--src", "renhost", "--dst", "renhost2"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg, "A host already exists with the name renhost2"
        )


###############################################################################
class test_cmd_replacevalue(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_replacevalue import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.key = AllowedKey(key="repval", validtype=1)
        self.key.save()
        self.host = Host(hostname="rephost")
        self.host.save()
        self.host2 = Host(hostname="rephost2")
        self.host2.save()
        self.kv = KeyValue(hostid=self.host, keyid=self.key, value="before")
        self.kv.save()
        self.kv2 = KeyValue(hostid=self.host2, keyid=self.key, value="before")
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
        namespace = self.parser.parse_args(["repval=before", "after", "rephost"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host, keyid=self.key)[0]
        self.assertEquals(kv.value, "after")

    ###########################################################################
    def test_badvalue(self):
        namespace = self.parser.parse_args(["repval=notexists", "newvalue", "rephost"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host, keyid=self.key)[0]
        self.assertEquals(kv.value, "before")

    ###########################################################################
    def test_badkey(self):
        namespace = self.parser.parse_args(["badkey=value", "newvalue", "rephost"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must use an existing key, not badkey")

    ###########################################################################
    def test_badexpr(self):
        namespace = self.parser.parse_args(["badexpr", "nobody", "cares"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "Must be in key=value format, not badexpr")

    ###########################################################################
    def test_nohosts(self):
        namespace = self.parser.parse_args(["repval=before", "after"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(
            cm.exception.msg, "Must specify a list of hosts or the --all flag"
        )

    ###########################################################################
    def test_all(self):
        namespace = self.parser.parse_args(["repval=before", "after", "--all"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kvlist = KeyValue.objects.filter(keyid=self.key)
        for k in kvlist:
            self.assertEquals(k.value, "after")

    ###########################################################################
    def test_kidding(self):
        """Test that it doesn't actually do anything in kidding mode"""
        namespace = self.parser.parse_args(["-k", "repval=before", "after", "rephost"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, (None, 0))
        kv = KeyValue.objects.filter(hostid=self.host, keyid=self.key)[0]
        self.assertEquals(kv.value, "before")


###############################################################################
class test_cmd_showkey(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_showkey import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)
        self.key1 = AllowedKey(
            key="showkey1", validtype=1, desc="description", restrictedFlag=True
        )
        self.key1.save()
        self.key2 = AllowedKey(
            key="showkey2",
            validtype=2,
            desc="another description",
            readonlyFlag=True,
            numericFlag=True,
        )
        self.key2.save()
        self.key3 = AllowedKey(key="showkey3", validtype=3, desc="")
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
            (
                "showkey1\tsingle\tdescription    [KEY RESTRICTED]\nshowkey2\tlist\tanother description    [NUMERIC][KEY READ ONLY]\nshowkey3\tdate\t    ",
                0,
            ),
        )

    ###########################################################################
    def test_showtype(self):
        namespace = self.parser.parse_args(["--type"])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output, ("showkey1\tsingle\nshowkey2\tlist\nshowkey3\tdate", 0)
        )

    ###########################################################################
    def test_showkeylist(self):
        namespace = self.parser.parse_args(["showkey1"])
        output = self.cmd.handle(namespace)
        self.assertEquals(
            output, ("showkey1\tsingle\tdescription    [KEY RESTRICTED]", 0)
        )

    ###########################################################################
    def test_showbadkeylist(self):
        namespace = self.parser.parse_args(["badkey"])
        with self.assertRaises(HostinfoException) as cm:
            self.cmd.handle(namespace)
        self.assertEquals(cm.exception.msg, "No keys to show")


###############################################################################
class test_cmd_undolog(TestCase):
    ###########################################################################
    def setUp(self):
        clearAKcache()
        import argparse
        from host.commands.cmd_hostinfo_undolog import Command

        self.cmd = Command()
        self.parser = argparse.ArgumentParser()
        self.cmd.parseArgs(self.parser)

    ###########################################################################
    def test_user(self):
        """Test normal behaviour for a user"""
        namespace = self.parser.parse_args(["--user", "foo"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output, ("", 0))

    ###########################################################################
    def test_week(self):
        """Test normal behaviour for a week"""
        namespace = self.parser.parse_args(["--week"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)

    ###########################################################################
    def test_days(self):
        """Test normal behaviour for 5 days"""
        namespace = self.parser.parse_args(["--days", "5"])
        output = self.cmd.handle(namespace)
        self.assertEquals(output[1], 0)

    ###########################################################################
    def test_undolog(self):
        """Test normal behaviour"""
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
        sys.argv = [
            "hostinfo_listalias",
        ]
        run_from_cmdline()

    ###########################################################################
    def test_badrun(self):
        sys.argv[0] = "notexists"
        rv = run_from_cmdline()
        self.assertEquals(rv, 255)
        errout = sys.stderr.getvalue()
        self.assertIn("No such hostinfo command notexists", errout)


# EOF
