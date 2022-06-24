#!/usr/bin/env python3
"""
Script to ping every host and update the 'lastping' key
to give an indication of 'liveness'
"""
# Writen by Dougal Scott <dougal.scott@gmail.com>

import argparse
import os
import subprocess
from multiprocessing import Pool


###############################################################################
def get_host_list(hostargs=""):
    """Get the list of hosts to check"""
    tmp = []
    cmd = f"hostinfo {hostargs}"
    with os.popen(cmd) as hinfh:
        for line in hinfh:
            hostname = line.strip()
            tmp.append(hostname)
    return tmp


###############################################################################
def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Ping everything")
    parser.add_argument(
        "--numthreads",
        action="store",
        type=int,
        help="Number of threads to run in parallel",
        default=None,
    )
    parser.add_argument(
        "--hostargs",
        action="store",
        help="Args to hostinfo to limit hosts",
        type=str,
        default="",
    )
    args = parser.parse_args()
    return args


###########################################################################
def pingCheck(hostname: str) -> bool:
    """Ping the hostname to see if it is up"""
    retcode = subprocess.call("/bin/ping", "-c", "1", hostname)
    if retcode < 0:
        return False
    return True


###########################################################################
def updateHost(hostname: str) -> None:
    """Update hostinfo with the new ping date"""
    subprocess.call(
        "hostinfo_addvalue",
        "--origin",
        "pingCheck",
        "--update",
        "lastping=today",
        hostname,
    )


###############################################################################
def pinger(hostname):
    """Check and update host if required"""
    print(hostname)
    if pingCheck(hostname):
        updateHost(hostname)


###############################################################################
def main():
    """mainline"""
    args = parse_args()
    host_list = get_host_list(args.hostargs)
    print(host_list)
    with Pool(args.numthreads) as pool:
        pool.map(pinger, host_list)


###############################################################################
if __name__ == "__main__":
    main()

# EOF
