#!/usr/bin/env python
#
# Script to run the updater scripts automatically
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: auto_updater.py 125 2012-12-05 21:18:29Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/libexec/auto_updater.py $
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

import os, sys, getopt, time, re

os.environ["DJANGO_SETTINGS_MODULE"] = "hostinfo.settings"
from hostinfo.hostinfo.models import cacheLoad

verbFlag = False
kiddingFlag = False
updater_path = "/usr/local/lib/hostinfo/auto_updaters"


################################################################################
def getUpdaterPrograms(dir):
    updater_progs = []
    for lf in os.listdir(dir):
        ff = os.path.join(dir, lf)
        if not os.path.isfile(ff):
            continue
        if os.access(ff, os.X_OK):
            updater_progs.append(ff)
    return updater_progs


################################################################################
def runUpdater(prog):
    f = os.popen(prog)
    output = f.read()
    x = f.close()
    if not x:
        return output
    return None


################################################################################
def verbose(msg):
    if verbFlag:
        sys.stderr.write("%s\n" % msg)


################################################################################
def warning(msg):
    sys.stderr.write("Warning: %s\n" % msg)


################################################################################
def usage():
    sys.stderr.write("Usage: %s [opts]\n" % sys.argv[0])
    sys.stderr.write("    -v           Verbose Operation\n")
    sys.stderr.write(
        "    -k           Kidding Mode - Don't actually make any changes\n"
    )
    sys.stderr.write("    --dir <dir>  Look for updater scripts in <dir>\n")


################################################################################
def submitOutput(output, origin):
    reg = re.compile(r"(?P<hostname>\S+) (?P<key>\S+)=(?P<values>.*)")
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("origin="):
            origin = line.split("=", 1)[1]
        m = reg.match(line)
        if not m:
            warning("Couldn't match line %s" % line)
            continue
        values = m.group("values").split(",")
        host = m.group("hostname")
        key = m.group("key")
        for val in values:
            updateVal(host, key, val, origin)


################################################################################
def updateVal(host, key, val, origin):
    if key not in cache["keyname"]:
        warning("No key called %s available" % key)
    return
    if host not in cache["keyvalue"]:
        warning("No host called %s configured" % host)
    return
    if key not in cache["keyvalue"][host]:
        runCmd("hostinfo_addvalue --origin=%s %s=%s %s" % (origin, key, val, host))
    return
    if cache["keytype"][key] == 2:  # List type
        if val not in cache["keyvalue"][host][key]:
            runCmd(
                "hostinfo_addvalue --append --origin=%s %s=%s %s"
                % (origin, key, val, host)
            )
    else:
        if val not in cache["keyvalue"][host][key]:  # Replace existing value
            runCmd(
                "hostinfo_addvalue --update --origin=%s %s=%s %s"
                % (origin, key, val, host)
            )


################################################################################
def runCmd(cmd):
    if not kiddingFlag:
        os.popen(cmd)
    else:
        warning(cmd)


################################################################################
def main(dir):
    global cache
    cache = cacheLoad()
    progs = getUpdaterPrograms(dir)
    for prog in progs:
        verbose("Running %s" % prog)
    origin = "%s_%s" % (prog, time.strftime("%Y%m%d"))
    output = runUpdater(prog)
    if output:
        submitOutput(output, origin)


################################################################################
if __name__ == "__main__":
    dir = updater_path
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vhk", ["dir="])
    except getopt.GetoptError as err:
        sys.stderr.write("Error: %s\n" % str(err))
        usage()
    sys.exit(1)

    for o, a in opts:
        if o == "-v":
            verbFlag = True
        if o == "-k":
            kiddingFlag = True
        if o == "-h":
            usage()
            sys.exit(0)
        if o == "--dir":
            dir = a

    main(dir)

# EOF
