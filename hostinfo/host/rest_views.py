from .models import Host, AllowedKey, KeyValue, HostAlias, Links, RestrictedValue
from .models import parseQualifiers, getMatches, getHost, HostinfoException
from .models import addKeytoHost
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


###############################################################################
@require_http_methods(["GET"])
def AliasList(request):
    aliases = get_list_or_404(HostAlias)
    ans = {'result': 'ok', 'aliases': [HostAliasSerialize(a, request) for a in aliases]}
    return JsonResponse(ans)


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
# /host/(hostname|pk)/key/(keyname|pk)[/value]
@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
def HostKeyRest(request, hostpk=None, hostname=None, keypk=None, key=None, value=None):
    result = 'ok'
    hostid = getReferredHost(hostpk, hostname)
    keyid = None

    # Get the id of the AllowedKey
    if keypk:
        ko = get_object_or_404(KeyValue, pk=keypk)
        keyid = ko.keyid
    if key:
        keyid = get_object_or_404(AllowedKey, key=key)

    if request.method == "GET":
        if not keyid:
            kvs = get_list_or_404(KeyValue, hostid=hostid)
        else:
            if keypk:
                kvs = get_list_or_404(KeyValue, hostid=hostid, pk=keypk)
            else:
                kvs = get_list_or_404(KeyValue, hostid=hostid, keyid=keyid)
        sha = [KeyValueSerialize(k, request) for k in kvs]
        return JsonResponse({'result': result, 'keyvalues': sha})
    elif request.method == "POST":
        if KeyValue.objects.filter(hostid=hostid, keyid=keyid, value=value):
            result = 'duplicate'
        elif KeyValue.objects.filter(hostid=hostid, keyid=keyid):
            result = 'updated'
            try:
                addKeytoHost(hostid=hostid, keyid=keyid, value=value, updateFlag=True)
            except HostinfoException as exc:
                result = 'failed %s' % str(exc)
        else:
            result = 'created'
            try:
                addKeytoHost(hostid=hostid, keyid=keyid, value=value)
            except HostinfoException as exc:
                result = 'failed %s' % str(exc)
    elif request.method == "DELETE":
        ha = get_object_or_404(KeyValue, hostid=hostid, keyid=keyid)
        ha.delete()
        result = 'deleted'

    kvals = []
    for h in KeyValue.objects.filter(hostid=hostid):
        kvals.append(KeyValueSerialize(h, request))
    return JsonResponse({'result': result, 'keyvalues': kvals})


###############################################################################
# /host/(hostname|pk)/link/(tagname|linkpk)[/url]
@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
def HostLinkRest(request, hostpk=None, hostname=None, linkpk=None, tagname=None, url=None):
    result = 'ok'
    hostid = getReferredHost(hostpk, hostname)

    # Get the id of the Link
    los = None
    if linkpk:
        los = Links.objects.filter(pk=linkpk)
    if tagname:
        los = Links.objects.filter(hostid=hostid, tag=tagname)
    if los:
        lo = los[0]
    else:
        lo = None

    if request.method == "GET":
        if not lo:
            links = get_list_or_404(Links, hostid=hostid)
        else:
            links = [lo]
        sha = [LinkSerialize(l, request) for l in links]
        return JsonResponse({'result': result, 'links': sha})
    elif request.method == "POST":
        if lo and lo.url == url:
            result = 'duplicate'
        elif lo and lo.url != url:
            result = 'updated'
            lo.url = url
            lo.save()
        else:
            result = 'created'
            lo = Links(hostid=hostid, tag=tagname, url=url)
            lo.save()
    elif request.method == "DELETE":
        if not lo:
            raise Http404("Link does not exist")
        lo.delete()
        result = 'deleted'

    links = []
    for h in Links.objects.filter(hostid=hostid):
        links.append(LinkSerialize(h, request))
    return JsonResponse({'result': result, 'links': links})


###############################################################################
@require_http_methods(["GET", "POST", "DELETE"])
@csrf_exempt
def HostAliasRest(request, hostpk=None, hostname=None, aliaspk=None, alias=None):
    result = 'ok'
    hostid = getReferredHost(hostpk, hostname)
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
def KeyDetail(request, akeypk=None, akey=None):
    if akeypk:
        keyid = get_object_or_404(AllowedKey, id=akeypk)
    elif akey:
        keyid = get_object_or_404(AllowedKey, key=akey)
    ans = {'result': 'ok', 'key': AllowedKeySerialize(keyid, request)}
    return JsonResponse(ans)


###############################################################################
@require_http_methods(["GET"])
def KValDetail(request, pk=None):
    keyid = get_object_or_404(KeyValue, id=pk)
    ans = {'result': 'ok', 'keyvalue': KeyValueSerialize(keyid, request)}
    return JsonResponse(ans)


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
        'hostname': obj.hostname,
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
        'url': request.build_absolute_uri(reverse('restakey', args=(obj.id,))),
        'key': obj.key,
        'validtype': obj.get_validtype_display(),
        'desc': obj.desc,
        'createdate': obj.createdate,
        'modifieddate': obj.modifieddate,
        'restricted': obj.restrictedFlag,
        'audit': obj.auditFlag
    }
    if obj.restrictedFlag:
        rvals = RestrictedValue.objects.filter(keyid=obj.id)
        ans['permitted_values'] = []
        for rv in rvals:
            ans['permitted_values'].append(RestrictedValueSerialize(rv, request))

    return ans


###############################################################################
def HostShortSerialize(obj, request):
    return {
        'hostid': obj.id,
        'hostname': obj.hostname,
        'url': request.build_absolute_uri(reverse('resthost', args=(obj.id,))),
    }


###############################################################################
def RestrictedValueSerialize(obj, request):
    ans = {
        'id': obj.id,
        'keyid': obj.keyid.id,
        'value': obj.value,
        'createdate': obj.createdate,
        'modifieddate': obj.modifieddate
    }
    return ans


###############################################################################
def LinkSerialize(obj, request):
    ans = {
        'id': obj.id,
        'host': HostShortSerialize(obj.hostid, request),
        'url': obj.url,
        'tag': obj.tag,
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
