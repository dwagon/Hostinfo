#
# Django models definition for hostinfo CMDB
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
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

from collections import defaultdict
from operator import itemgetter
from django.db import models, connection
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from simple_history.models import HistoricalRecords
import argparse
import os
import re
import sys
import time

_akcache = {None: None}
_all_hosts = None
_all_hosts_cache_time = None


################################################################################
class HostinfoException(Exception):
    def __init__(self, msg="", retval=1):
        self.msg = msg
        self.retval = retval

    def __str__(self):  # pragma: no cover
        return repr(self.msg)


################################################################################
class ReadonlyValueException(HostinfoException):
    """A change has been attempted on a read only value"""

    def __init__(self, key=None, msg="", retval=2):
        self.key = key
        self.msg = msg
        self.retval = retval

    def __str__(self):  # pragma: no cover
        return repr(self.msg)


################################################################################
class RestrictedValueException(HostinfoException):
    """A change has been attempted on a restricted value"""

    def __init__(self, msg, key=None, retval=3):
        self.msg = msg
        self.key = key
        self.retval = retval

    def __str__(self):  # pragma: no cover
        return repr(self.msg)


################################################################################
class HostinfoInternalException(HostinfoException):  # pragma: no cover
    """Something screwy has gone on that was unexpected in the code"""

    def __init__(self, key=None, msg="", retval=255):
        self.key = key
        self.msg = msg
        self.retval = retval


################################################################################
def getUser(instance=None):
    """Get the user for the audittrail
    For command line access use the persons login name
    """
    username = user = None
    try:
        username = os.getlogin()
    except OSError:
        username = "unknown"
    if username and user is None:
        user, created = User.objects.get_or_create(username=username)
    return user.username[:20]


############################################################################
def auditedKey(instance):
    """Return True if the AllowKey should be audited"""
    return instance.keyid.auditFlag


################################################################################
################################################################################
################################################################################
class Host(models.Model):
    hostname = models.CharField(max_length=200, unique=True)
    origin = models.CharField(max_length=200, blank=True)
    createdate = models.DateField(auto_now_add=True)
    modifieddate = models.DateField(auto_now=True)
    docpage = models.URLField(blank=True, null=True)
    history = HistoricalRecords()

    ############################################################################
    def save(self, user=None, **kwargs):
        global _all_hosts
        if not user:
            user = getUser()
        self.hostname = self.hostname.lower()
        if not self.id:  # Check for update
            undo = UndoLog(
                user=user, action="hostinfo_deletehost --lethal %s" % self.hostname
            )
            undo.save()
        super(Host, self).save(**kwargs)
        _all_hosts = None

    ############################################################################
    def delete(self, user=None):
        global _all_hosts
        if not user:
            user = getUser()
        undo = UndoLog(user=user, action="hostinfo_addhost %s" % self.hostname)
        undo.save()
        super(Host, self).delete()
        _all_hosts = None

    ############################################################################
    def __str__(self):  # pragma: no cover
        return "%s" % self.hostname

    ############################################################################
    class Meta:
        ordering = ["hostname"]


################################################################################
################################################################################
################################################################################
class HostAlias(models.Model):
    hostid = models.ForeignKey(
        Host, db_index=True, related_name="aliases", on_delete=models.CASCADE
    )
    alias = models.CharField(max_length=200, unique=True)
    origin = models.CharField(max_length=200, blank=True)
    createdate = models.DateField(auto_now_add=True)
    modifieddate = models.DateField(auto_now=True)
    history = HistoricalRecords()

    ############################################################################
    def __str__(self):  # pragma: no cover
        return "%s -> %s" % (self.alias, self.hostid.hostname)

    ############################################################################
    class Meta:
        pass


################################################################################
################################################################################
################################################################################
class AllowedKey(models.Model):
    key = models.CharField(max_length=200)
    TYPE_CHOICES = ((1, "single"), (2, "list"), (3, "date"))
    validtype = models.IntegerField(choices=TYPE_CHOICES, default=1)
    desc = models.CharField(max_length=250, blank=True)
    createdate = models.DateField(auto_now_add=True)
    modifieddate = models.DateField(auto_now=True)
    restrictedFlag = models.BooleanField(default=False)
    readonlyFlag = models.BooleanField(default=False)
    auditFlag = models.BooleanField(default=True)
    numericFlag = models.BooleanField(default=False)
    reservedFlag2 = models.BooleanField(default=True)
    docpage = models.URLField(blank=True, null=True)
    history = HistoricalRecords()

    ############################################################################
    def __str__(self):  # pragma: no cover
        return "%s" % self.key

    ############################################################################
    class Meta:
        ordering = ["key"]


################################################################################
################################################################################
################################################################################
class KeyValue(models.Model):
    hostid = models.ForeignKey(Host, db_index=True, on_delete=models.CASCADE)
    keyid = models.ForeignKey(AllowedKey, db_index=True, on_delete=models.CASCADE)
    value = models.CharField(max_length=200, blank=True)
    numvalue = models.FloatField(null=True)
    origin = models.CharField(max_length=200, blank=True)
    createdate = models.DateField(auto_now_add=True)
    modifieddate = models.DateField(auto_now=True)
    history = HistoricalRecords()

    ############################################################################
    def save(self, user=None, readonlychange=False, **kwargs):
        if not user:
            user = getUser()
        self.value = self.value.lower().strip()
        if not self.value:
            raise HostinfoException("Empty value not permitted")
        try:
            self.numvalue = float(self.value)
        except ValueError:
            self.numvalue = None
        # Check to see if we are restricted
        if self.keyid.restrictedFlag:
            rk = RestrictedValue.objects.filter(keyid=self.keyid, value=self.value)
            if not rk:
                raise RestrictedValueException(
                    key=self.keyid, msg="%s is a restricted key" % self.keyid
                )

        if self.keyid.readonlyFlag and not readonlychange:
            raise ReadonlyValueException(
                key=self.keyid, msg="%s is a readonly key" % self.keyid
            )
        if self.keyid.get_validtype_display() == "date":
            self.value = validateDate(self.value)

        if self.id:  # Check for update
            oldobj = KeyValue.objects.get(id=self.id)
            undo = UndoLog(
                user=user,
                action="hostinfo_replacevalue %s=%s %s %s"
                % (self.keyid, self.value, oldobj.value, self.hostid),
            )
            undo.save()
        else:  # New object
            undo = UndoLog(
                user=user,
                action="hostinfo_deletevalue %s=%s %s"
                % (self.keyid, self.value, self.hostid),
            )
            undo.save()

        # Actually do the saves
        if not self.keyid.auditFlag:
            self.skip_history_when_saving = True
        super(KeyValue, self).save(**kwargs)

    ############################################################################
    def delete(self, user=None, readonlychange=False):
        if not user:
            user = getUser()
        if self.keyid.readonlyFlag and not readonlychange:
            raise ReadonlyValueException(
                key=self.keyid, msg="%s is a read only key" % self.keyid
            )
        if self.keyid.get_validtype_display() == "list":
            undoflag = "--append"
        else:
            undoflag = ""
        undo = UndoLog(
            user=user,
            action="hostinfo_addvalue %s %s=%s %s"
            % (undoflag, self.keyid, self.value, self.hostid),
        )
        undo.save()
        super(KeyValue, self).delete()

    ############################################################################
    def __str__(self):  # pragma: no cover
        return "%s=%s" % (self.keyid.key, self.value)

    ############################################################################
    class Meta:
        unique_together = (("hostid", "keyid", "value"),)


################################################################################
################################################################################
################################################################################
class UndoLog(models.Model):
    user = models.CharField(max_length=200)
    actiondate = models.DateTimeField(auto_now=True)
    action = models.CharField(max_length=200)

    ############################################################################
    class Meta:
        pass

    ############################################################################
    def save(self, **kwargs):
        if hasattr(self.user, "username"):
            self.user.username = self.user.username[:200]
        else:
            self.user = self.user[:200]
        self.action = self.action[:200]
        super(UndoLog, self).save(**kwargs)


################################################################################
################################################################################
################################################################################
class RestrictedValue(models.Model):
    """If an AllowedKey is restricted then the value can only be one that appears
    in this table
    """

    keyid = models.ForeignKey(AllowedKey, db_index=True, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    createdate = models.DateField(auto_now_add=True)
    modifieddate = models.DateField(auto_now=True)
    history = HistoricalRecords()

    ############################################################################
    def __str__(self):  # pragma: no cover
        return "%s %s" % (self.keyid.key, self.value)

    ############################################################################
    class Meta:
        unique_together = (("keyid", "value"),)


################################################################################
################################################################################
################################################################################
class Links(models.Model):
    hostid = models.ForeignKey(
        Host, db_index=True, related_name="links", on_delete=models.CASCADE
    )
    url = models.CharField(max_length=200)
    tag = models.CharField(max_length=100)
    modifieddate = models.DateField(auto_now=True)
    history = HistoricalRecords()

    ############################################################################
    class Meta:
        ordering = ["hostid", "tag"]


############################################################################
def validateDate(datestr):
    """Convert the various dates to a single format: YYYY-MM-DD"""
    year = -1
    month = -1
    day = -1

    # Check if people are using a shortcut
    if datestr in ("today", "now"):
        year = time.localtime()[0]
        month = time.localtime()[1]
        day = time.localtime()[2]
        return "%04d-%02d-%02d" % (year, month, day)

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d/%m/%y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            newdate = time.strptime(datestr, fmt)
        except ValueError:
            continue
        year = newdate[0]
        month = newdate[1]
        day = newdate[2]
        break

    if year < 0:
        raise TypeError(
            "%s couldn't be converted to a known date format (e.g. YYYY-MM-DD)"
            % datestr
        )

    return "%04d-%02d-%02d" % (year, month, day)


################################################################################
def parseQualifiers(args):
    """
    Go through the supplied qualifiers and analyse them, generate
    a list of qualifier tuples: operator, key, value
    """

    # Table of all the operators:
    #    tag of operator, regexp, threepart (ie. has value)?
    optable = [
        ("unequal", "!=|\.ne\.", {"threeparts": True}),
        ("equal", "=|\.eq\.", {"threeparts": True}),  # Has to be after !=
        ("lessthan", "<|\.lt\.", {"threeparts": True}),
        ("greaterthan", ">|\.gt\.", {"threeparts": True}),
        ("contains", "~|\.ss\.", {"threeparts": True}),
        ("notcontains", "%|\.ns\.", {"threeparts": True}),
        ("approx", "@|\.ap\.", {"threeparts": True}),
        ("undef", "\.undef|\.undefined|\.unset", {"threeparts": False}),
        ("def", "\.def|\.defined|\.set", {"threeparts": False}),
        ("hostre", "\.hostre", {"threeparts": False, "validkey": False}),
        ("lenlt", "\.lenlt\.", {"threeparts": True}),
        ("leneq", "\.leneq\.", {"threeparts": True}),
        ("lengt", "\.lengt\.", {"threeparts": True}),
    ]

    qualifiers = []
    for arg in args:
        if arg == "":
            continue
        matched = False
        # Check to make sure that the qualifier isn't actually a host with an
        # embedded operator like subdomain - e.g. host.lt.example.com
        ishostname = Host.objects.filter(hostname=arg.lower())
        if ishostname:
            qualifiers.append(("host", None, arg.lower()))
            matched = True
            continue
        for op, reg, opts in optable:
            if opts["threeparts"]:
                mo = re.match("(?P<key>.+)(%s)(?P<val>.+)" % reg, arg)
            else:
                mo = re.match("(?P<key>.+)(%s)(?P<val>)" % reg, arg)
            if mo:
                key = mo.group("key").lower()
                if opts.get("validkey", True):
                    getAK(key)
                val = mo.group("val").lower()
                if opts["threeparts"]:
                    if getAK(key).get_validtype_display() == "date":
                        val = validateDate(val)
                qualifiers.append((op, key, val))
                matched = True
                break

        if not matched:
            hm = re.match("\w+", arg)
            if hm:
                qualifiers.append(("host", None, arg.lower()))
                matched = True

        if not matched:
            raise HostinfoException("Unknown qualifier %s" % arg)

    return qualifiers


################################################################################
def calcKeylistVals(key, from_hostids=[]):
    keyid = getAK(key)
    kvlist = KeyValue.objects.filter(keyid__key=key).values_list(
        "hostid", "value", "numvalue"
    )
    if not from_hostids:
        from_hostids = [v[0] for v in get_all_hosts().values_list("id")]
    total = len(from_hostids)

    # Calculate the number of times each value occurs
    values = defaultdict(int)
    hostids = set()
    for hostid, value, numvalue in kvlist:
        if hostid not in from_hostids:
            continue
        hostids.add(hostid)
        if keyid.numericFlag:
            values[(value, numvalue)] += 1
        else:
            values[(value, None)] += 1
    numdef = len(hostids)

    # Calculate for each distinct value the percentages
    tmpvalues = []
    for k, v in list(values.items()):
        p = 100.0 * v / numdef
        tmpvalues.append((k[0], k[1], v, p))
        # (strval, numval), count, pct

    if keyid.numericFlag:
        tv = sorted(tmpvalues, key=itemgetter(1, 0))
    else:
        tv = sorted(tmpvalues, key=itemgetter(0))
    numundef = total - numdef
    if not isinstance(key, str):
        key = str(key)
    d = {
        "key": key,
        "vallist": [(val, count, pct) for [val, numval, count, pct] in tv],
        "numvals": len(tmpvalues),
        "numdef": numdef,
        "pctdef": 100.0 * numdef / total,
        "numundef": numundef,
        "pctundef": 100.0 * numundef / total,
        "total": total,
    }
    return d


################################################################################
def oneoff(val):
    """Copied from norvig.com/spell-correct.html
    A page of true awesomeness
    """
    import string

    alphabet = string.ascii_lowercase + string.digits
    s = [(val[:i], val[i:]) for i in range(len(val) + 1)]
    deletes = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts = [a + c + b for a, b in s for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


################################################################################
def getApproxObjects(keyid, value):
    """Return all of the hostids that have a value that is approximately
    value
    """
    vals = KeyValue.objects.filter(keyid=keyid)
    approxans = set()
    approx = oneoff(value)
    for v in vals:
        if v.value in approx:
            approxans.add(v)
    ans = [{"hostid": v.hostid.id} for v in approxans]
    return ans


################################################################################
def get_all_hosts():
    global _all_hosts
    global _all_hosts_cache_time
    if _all_hosts is None or _all_hosts_cache_time < time.time() - 60:
        _all_hosts = Host.objects.all()
        _all_hosts_cache_time = time.time()
    return _all_hosts


################################################################################
def getHostList(criteria):
    allhosts = {}
    for host in get_all_hosts():
        allhosts[host.id] = host

    qualifiers = parseQualifiers(criteria)
    hostids = getMatches(qualifiers)
    hosts = [allhosts[hid] for hid in hostids]
    return hosts


################################################################################
def getMatches(qualifiers):
    """Get a list of matching hostids that satisfy the qualifiers

    Create a set of all the hostids and then go through each qualifier
    and create a set of hostids that match that qualifier and then
    take the intersection of those sets to get the hosts that match
    the qualifier.

    Unequal queries are handled a bit differently by taking the
    difference between all hosts and the hosts that have that value set.
    """
    hostids = set([host.id for host in get_all_hosts()])
    for q, k, v in qualifiers:  # qualifier, key, value
        if q != "hostre":  # hostre doesn't put a key into key
            key = getAK(k)
            checknum = False
            # Numeric keys can be queried for non-numeric values
            if key and key.numericFlag:
                try:
                    float(v)
                    checknum = True
                except ValueError:
                    pass
        mode = "intersection"
        queryset = set([])  # Else if no match it won't have a queryset defined
        if q == "host":
            hostqs = set([h.id for h in Host.objects.filter(hostname=v)])
            aliasqs = set([ha.hostid.id for ha in HostAlias.objects.filter(alias=v)])
            queryset = hostqs | aliasqs
            vals = []
        elif q == "equal":
            if checknum:
                vals = KeyValue.objects.filter(keyid=key.id, numvalue=v).values(
                    "hostid"
                )
            else:
                vals = KeyValue.objects.filter(keyid=key.id, value=v).values("hostid")
        elif q == "lessthan":
            if checknum:
                vals = KeyValue.objects.filter(keyid=key.id, numvalue__lt=v).values(
                    "hostid"
                )
            else:
                vals = KeyValue.objects.filter(keyid=key.id, value__lt=v).values(
                    "hostid"
                )
        elif q == "approx":
            vals = getApproxObjects(keyid=key.id, value=v)
        elif q == "greaterthan":
            if checknum:
                vals = KeyValue.objects.filter(keyid=key.id, numvalue__gt=v).values(
                    "hostid"
                )
            else:
                vals = KeyValue.objects.filter(keyid=key.id, value__gt=v).values(
                    "hostid"
                )
        elif q == "contains":
            vals = KeyValue.objects.filter(keyid=key.id, value__contains=v).values(
                "hostid"
            )
        elif q == "notcontains":
            vals = KeyValue.objects.filter(keyid=key.id, value__contains=v).values(
                "hostid"
            )
            mode = "difference"
        elif q == "def":
            vals = KeyValue.objects.filter(keyid=key.id).values("hostid")
        elif q == "unequal":
            if checknum:
                vals = KeyValue.objects.filter(keyid=key.id, numvalue=v).values(
                    "hostid"
                )
            else:
                vals = KeyValue.objects.filter(keyid=key.id, value=v).values("hostid")
            mode = "difference"
        elif q == "undef":
            vals = KeyValue.objects.filter(keyid=key.id).values("hostid")
            mode = "difference"
        if q in ("leneq", "lengt", "lenlt"):
            vals = []
            mode = "noop"
        elif q == "hostre":
            vals = [
                {"hostid": h["id"]}
                for h in Host.objects.filter(hostname__contains=k).values("id")
            ]
            alias = [
                {"hostid": h["hostid"]}
                for h in HostAlias.objects.filter(alias__contains=k).values("hostid")
            ]
            vals.extend(alias)

        if vals:
            queryset = set([e["hostid"] for e in vals])
        if mode == "intersection":
            hostids = hostids & queryset
        elif mode == "difference":
            hostids = hostids - queryset
        elif mode == "noop":
            pass

    # Some queries require post processing
    # Note that these are much slower to process so do them after
    for q, k, v in qualifiers:  # qualifier, key, value
        if q in ("leneq", "lengt", "lenlt"):
            key = getAK(k)
            try:
                lngth = int(v)
            except ValueError:
                raise HostinfoException("Length must be an integer, not %s" % str(v))
            for h in get_all_hosts():
                if h.id not in hostids:
                    continue
                vals = KeyValue.objects.filter(hostid=h.id, keyid=key.id)
                if q == "leneq":
                    if len(vals) != lngth:
                        hostids.remove(h.id)
                elif q == "lengt":
                    if len(vals) < lngth:
                        hostids.remove(h.id)
                elif q == "lenlt":
                    if len(vals) > lngth:
                        hostids.remove(h.id)

    return list(hostids)


################################################################################
def getAliases(hostname):
    """Return the list of aliases that this host has"""
    aliaslist = HostAlias.objects.filter(hostid__hostname=hostname)
    return [a.alias for a in aliaslist]


################################################################################
def getHost(hostname):
    """Return the host object based on the hostname either from the Host or the
    HostAlias. Return None if not found
    """
    try:
        h = Host.objects.get(hostname=hostname)
    except ObjectDoesNotExist:
        pass
    else:
        return h

    try:
        ha = HostAlias.objects.get(alias=hostname)
        h = Host.objects.get(hostname=ha.hostid.hostname)
    except ObjectDoesNotExist:
        pass
    else:
        return h

    return None


################################################################################
def getOrigin(origin):
    """Standard 'origin' getter
    Use the origin variable if provided otherwise try and determine who
    is making the change
    """
    if origin:
        return origin
    try:
        origin = os.getlogin()
    except OSError:  # pragma: no cover
        # Web interface can't do os.getlogin calls
        for e in ("REMOTE_USER", "REMOTE_ADDR", "USER"):
            try:
                origin = os.environ[e]
            except KeyError:
                pass
            else:
                break
    if not origin:  # pragma: no cover
        origin = "unknown"
    return origin


################################################################################
def checkHost(host):
    """Check to make sure that a host exists"""
    h = Host.objects.filter(hostname=host)
    if h:
        return True
    else:
        return False


################################################################################
def clearAKcache():
    """Remove the contents of the allowedkey cache - mostly for test purposes"""
    global _akcache
    _akcache = {None: None}


################################################################################
def getAK(key):
    """Lookup AllowedKeys. This is a oft repeated expensive activity so
    cache it"""
    global _akcache
    if key not in _akcache:
        try:
            _akcache[key] = AllowedKey.objects.get(key=key)
        except ObjectDoesNotExist:
            raise HostinfoException("Must use an existing key, not %s" % key)
    return _akcache[key]


################################################################################
def addKeytoHost(
    host=None,
    hostid=None,
    key=None,
    keyid=None,
    value="",
    origin=None,
    updateFlag=False,
    readonlyFlag=False,
    appendFlag=False,
):
    retval = 0
    if not keyid:
        keyid = getAK(key)
    if not hostid:
        hostid = getHost(host)
    origin = getOrigin(origin)
    if not hostid:
        raise HostinfoException("Unknown host: %s" % host)
    keytype = keyid.get_validtype_display()
    if keytype != "list" and appendFlag:
        raise HostinfoException("Can only append to list type keys")
    kv = KeyValue.objects.filter(hostid=hostid, keyid=keyid)
    if kv:  # Key already exists
        if updateFlag:
            kv[0].value = value
            kv[0].origin = origin
            kv[0].save(readonlychange=readonlyFlag)
        elif appendFlag:
            checkkv = KeyValue.objects.filter(hostid=hostid, keyid=keyid, value=value)
            if not checkkv:
                newkv = KeyValue(hostid=hostid, origin=origin, keyid=keyid, value=value)
                newkv.save(readonlychange=readonlyFlag)
                retval = 0
        else:
            if kv[0].value != value:
                raise HostinfoException(
                    "%s:%s already has a value %s" % (host, key, kv[0].value)
                )
            else:
                retval = 1
    else:
        newkv = KeyValue(hostid=hostid, origin=origin, keyid=keyid, value=value)
        newkv.save(readonlychange=readonlyFlag)
    return retval


###############################################################################
class HostinfoCommand(object):
    description = None
    epilog = None

    def over_parseArgs(self):
        parser = argparse.ArgumentParser(
            description=self.description, epilog=self.epilog
        )
        self.parseArgs(parser)
        self.namespace = parser.parse_args(sys.argv[1:])

    def over_handle(self):
        return self.handle(self.namespace)


###############################################################################
def run_from_cmdline():
    import importlib

    start_time = time.time()
    cmdname = "host.commands.cmd_%s" % os.path.basename(sys.argv[0])
    try:
        cmd = importlib.import_module(cmdname)
    except ImportError:
        sys.stderr.write("No such hostinfo command %s\n" % sys.argv[0])
        return 255
    c = cmd.Command()
    c.over_parseArgs()
    try:
        output, retval = c.over_handle()
        if output is not None:
            print(output.strip())
    except HostinfoException as exc:
        sys.stderr.write("%s\n" % exc.msg)
        return exc.retval
    if settings.DEBUG:  # pragma: no cover
        end_time = time.time()
        db_query_time = sum([float(x["time"]) for x in connection.queries])
        sys.stderr.write(
            "DB Queries: %d queries in %f secs.\n"
            % (len(connection.queries), db_query_time)
        )
        sys.stderr.write("Total time %f secs\n" % (end_time - start_time))
    return retval


# EOF
