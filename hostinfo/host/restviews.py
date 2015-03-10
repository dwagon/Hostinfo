from .models import Host, AllowedKey, KeyValue, HostAlias, Links
from .models import parseQualifiers, getMatches, getHost, HostinfoException
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


###############################################################################
@require_http_methods(["GET"])
def HostQuery(request, query):
    criteria = query.split('/')
    try:
        qualifiers = parseQualifiers(criteria)
    except HostinfoException as exc:
        return JsonResponse({'error': str(exc)}, status=406)
    matches = getMatches(qualifiers)
    hosts = [Host.objects.get(id=pk) for pk in matches]
    ans = {
        'result': '%d matching hosts' % len(hosts),
        'hosts': [HostShortSerialize(h, request) for h in hosts],
    }
    return JsonResponse(ans)


###############################################################################
@require_http_methods(["GET"])
def HostDetail(request, hostpk=None, hostname=None):
    hostid = getReferredHost(hostpk, hostname)
    ans = {'result': 'ok', 'host': HostSerialize(hostid, request)}
    return JsonResponse(ans)


###############################################################################
def getReferredHost(hostpk=None, hostname=None):
    if hostpk:
        hostid = get_object_or_404(Host, id=hostpk)
    elif hostname:
        hostid = getHost(hostname=hostname)
        if not hostid:
            raise Http404("Host %s does not exist" % hostname)
    return hostid


###############################################################################
@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
def HostAliasRest(request, pk=None, name=None, aliaspk=None, alias=None):
    status = 'ok'
    hostid = getReferredHost(pk, name)
    if request.method == "GET":
        if not alias:
            ha = get_list_or_404(HostAlias, hostid=hostid)
        else:
            if aliaspk:
                ha = get_list_or_404(HostAlias, hostid=hostid, pk=aliaspk)
            else:
                ha = get_list_or_404(HostAlias, hostid=hostid, alias=alias)
        sha = [HostAliasSerialize(h, request) for h in ha]
        ans = {'result': result, 'aliases': sha}
        return JsonResponse(ans)
    elif request.method == "POST":
        if HostAlias.objects.filter(hostid=hostid, alias=alias):
            result = 'duplicate'
        else:
            ha = HostAlias(hostid=hostid, alias=alias)
            ha.save()
            result = 'created'
    elif request.method == "DELETE":
        ha = get_object_or_404(HostAlias, hostid=hostid, alias=alias)
        ha.delete()
        result = 'deleted'

    aliases = []
    for h in HostAlias.objects.filter(hostid=hostid):
        aliases.append(HostAliasSerialize(h, request))
    ans = {'aliases': aliases, 'result': result}
    return JsonResponse(ans)


###############################################################################
@require_http_methods(["GET"])
def HostList(request):
    hosts = get_list_or_404(Host)
    ans = {'result': '%d hosts' % len(hosts), 'hosts': [HostShortSerialize(h, request) for h in hosts]}
    return JsonResponse(ans)


###############################################################################
@require_http_methods(["GET"])
def KeyDetail(request, pk=None, name=None):
    if pk:
        keyid = get_object_or_404(AllowedKey, id=pk)
    elif name:
        keyid = get_object_or_404(AllowedKey, key=name)
    return JsonResponse(AllowedKeySerialize(keyid, request))


###############################################################################
@require_http_methods(["GET"])
def KValDetail(request, pk=None):
    keyid = get_object_or_404(KeyValue, id=pk)
    return JsonResponse(KeyValueSerialize(keyid, request))


###############################################################################
def HostSerialize(obj, request):
    keys = {}
    for ak in AllowedKey.objects.all():
        keys[ak.id] = ak.key
    keyvals = {}
    for k in KeyValue.objects.filter(hostid=obj):
        keyname = keys[k.keyid_id]
        if keyname not in keyvals:
            keyvals[keyname] = []
        keyvals[keyname].append(KeyValueSerialize(k, request))

    aliases = []
    for h in HostAlias.objects.filter(hostid=obj):
        aliases.append(HostAliasSerialize(h, request))
    links = []
    for l in Links.objects.filter(hostid=obj):
        links.append(LinkSerialize(l, request))

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
def AllowedKeySerialize(obj, request):
    ans = {
        'id': obj.id,
        'url': request.build_absolute_uri(reverse('restkey', args=(obj.id,))),
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
def HostShortSerialize(obj, request):
    return {
        'hostid': obj.id,
        'hostname': obj.hostname,
        'url': request.build_absolute_uri(reverse('resthost', args=(obj.id,))),
    }


###############################################################################
def LinkSerialize(obj, request):
    ans = {
        'id': obj.id,
        'host': HostShortSerialize(obj.hostid, request),
        'url': obj.url,
        'tag': obj.url,
        'modifieddate': obj.modifieddate
    }
    return ans


###############################################################################
def KeyValueSerialize(obj, request):
    ans = {
        'id': obj.id,
        'url': request.build_absolute_uri(reverse('restkval', args=(obj.id,))),
        'host': HostShortSerialize(obj.hostid, request),
        'keyid': obj.keyid.id,
        'key': obj.keyid.key,
        'value': obj.value,
        'origin': obj.origin,
        'createdate': obj.createdate,
        'modifieddate': obj.modifieddate
    }
    return ans


###############################################################################
def HostAliasSerialize(obj, request):
    ans = {
        'id': obj.id,
        'url': request.build_absolute_uri(reverse('hostaliasrest', args=(obj.hostid.hostname, obj.id,))),
        'host': HostShortSerialize(obj.hostid, request),
        'alias': obj.alias,
        'origin': obj.origin,
        'createdate': obj.createdate,
        'modifieddate': obj.modifieddate
        }
    return ans

# EOF
