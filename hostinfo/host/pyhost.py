# Library of functions to access hostinfo from within a python script
# instead of requiring to call shell scripts and parse the results
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id$
# $HeadURL$

import sys

from django.core.management import setup_environ
from hostinfo import settings
setup_environ(settings)
from .models import getMatches, parseQualifiers
from .models import KeyValue, Host

################################################################################
def getHostinfo(*args, **kwargs):
    """ Return a dictionary of dictionaries for each hostinfo host that matches the
    args/kwargs.
    Call like:
        getHostinfo(environment='uat')
        getHostinfo('os!=linux')
        { 'hostA': { 'keyA': ['val1', 'val2'], 'keyB': ['val2']}, 'hostB': {...}}
    """
    args=list(args)
    ans={}
    for k,v in kwargs.items():
        args.append("%s=%s" % (k,v))
    qualifiers=parseQualifiers(args)
    matches=getMatches(qualifiers)
    for hostid in matches:
        host={}
        hostname=Host.objects.get(id=hostid).hostname
        for k in KeyValue.objects.filter(hostid=hostid):
            keyname=k.keyid.key
            if keyname not in host:
                host[keyname]=[]             
            host[keyname].append(k.value)
        ans[hostname]=host
    return ans

#EOF
