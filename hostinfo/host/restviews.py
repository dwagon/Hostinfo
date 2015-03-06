from .models import Host, AllowedKey, KeyValue, HostAlias, Links
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse


###############################################################################
def HostDetail(request, pk=None, name=None):
    if pk:
        hostid = get_object_or_404(Host, id=pk)
    elif name:
        hostid = get_object_or_404(Host, hostname=name)
    return JsonResponse(HostSerialize(hostid))


###############################################################################
def KeyDetail(request, pk=None, name=None):
    if pk:
        keyid = get_object_or_404(AllowedKey, id=pk)
    elif name:
        keyid = get_object_or_404(AllowedKey, key=name)
    return JsonResponse(AllowedKeySerialize(keyid))


###############################################################################
def AliasDetail(request, pk=None, name=None):
    if pk:
        keyid = get_object_or_404(HostAlias, id=pk)
    elif name:
        keyid = get_object_or_404(HostAlias, alias=name)
    return JsonResponse(HostAliasSerialize(keyid))


###############################################################################
def KValDetail(request, pk=None):
    keyid = get_object_or_404(KeyValue, id=pk)
    return JsonResponse(KeyValueSerialize(keyid))


###############################################################################
def HostSerialize(obj):
    keys = {}
    for ak in AllowedKey.objects.all():
        keys[ak.id] = ak.key
    keyvals = {}
    for k in KeyValue.objects.filter(hostid=obj):
        keyname = keys[k.keyid_id]
        if keyname not in keyvals:
            keyvals[keyname] = []
        keyvals[keyname].append(KeyValueSerialize(k))

    aliases = []
    for h in HostAlias.objects.filter(hostid=obj):
        aliases.append(HostAliasSerialize(h))
    links = []
    for l in Links.objects.filter(hostid=obj):
        links.append(LinkSerialize(l))

    ans = {
        'id': obj.id,
        'name': obj.hostname,
        'origin': obj.origin,
        'createdate': obj.createdate,
        'modifieddate': obj.modifieddate,
        'keyvalues': keyvals,
        'aliases': aliases,
        'links': links,
        }
    return ans


###############################################################################
def AllowedKeySerialize(obj):
    ans = {
        'id': obj.id,
        'url': reverse('restkey', args=(obj.id,)),
        'key': obj.key,
        'validtype': obj.get_validtype_display(),
        'desc': obj.desc,
        'createdate': obj.createdate,
        'modifieddate': obj.modifieddate,
        'restricted': obj.restrictedFlag,
        'audit': obj.auditFlag
    }
    return ans


###############################################################################
def HostShortSerialize(obj):
    return {
        'hostid': obj.id,
        'hostname': obj.hostname,
        'url': reverse('resthost', args=(obj.id,)),
    }


###############################################################################
def LinkSerialize(obj):
    ans = {
        'id': obj.id,
        'host': HostShortSerialize(obj.hostid),
        'url': obj.url,
        'tag': obj.url,
        'modifieddate': obj.modifieddate
    }
    return ans


###############################################################################
def KeyValueSerialize(obj):
    ans = {
        'id': obj.id,
        'url': reverse('restkval', args=(obj.id,)),
        'host': HostShortSerialize(obj.hostid),
        'keyid': obj.keyid.id,
        'key': obj.keyid.key,
        'value': obj.value,
        'origin': obj.origin,
        'createdate': obj.createdate,
        'modifieddate': obj.modifieddate
    }
    return ans


###############################################################################
def HostAliasSerialize(obj):
    ans = {
        'id': obj.id,
        'url': reverse('restalias', args=(obj.id,)),
        'host': HostShortSerialize(obj.hostid),
        'alias': obj.alias,
        'origin': obj.origin,
        'createdate': obj.createdate,
        'modifieddate': obj.modifieddate
        }
    return ans

# EOF
