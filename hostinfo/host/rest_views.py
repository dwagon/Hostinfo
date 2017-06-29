from .models import Host, AllowedKey, KeyValue, HostAlias, Links, RestrictedValue
from .models import parseQualifiers, getMatches, getHost, HostinfoException
from .models import addKeytoHost, calcKeylistVals
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json


###############################################################################
@require_http_methods(["GET"])
def AliasList(request, *args):
    aliases = get_list_or_404(HostAlias)
    ans = {'result': 'ok', 'aliases': [HostAliasSerialize(a, request) for a in aliases]}
    return JsonResponse(ans)


###############################################################################
def getSerializerArgs(request):
    sargs = {'keys': False, 'links': False, 'aliases': False, 'dates': False, 'origin': False}
    payload = get_payload(request)
    if 'keys' in payload:
        sargs['keys'] = payload['keys']
    if 'links' in payload:
        sargs['links'] = True
    if 'aliases' in payload:
        sargs['aliases'] = True
    if 'dates' in payload:
        sargs['dates'] = True
    if 'origin' in payload:
        sargs['origin'] = True
    return sargs


###############################################################################
@require_http_methods(["GET"])
def HostQuery(request, query):
    sargs = getSerializerArgs(request)
    criteria = query.split('/')
    try:
        qualifiers = parseQualifiers(criteria)
    except HostinfoException as exc:    # pragma: no cover
        return JsonResponse({'error': str(exc)}, status=406)
    matches = getMatches(qualifiers)
    hosts = [Host.objects.get(id=pk) for pk in matches]
    ans = {
        'result': '%d matching hosts' % len(hosts),
        'hosts': [HostSerialize(h, request, **sargs) for h in hosts],
    }
    return JsonResponse(ans)


###############################################################################
def get_payload(request):
    body_unicode = request.body.decode('utf-8')
    data = {}
    for k, v in request.GET.items():
        data[k] = v.split(',')
    try:
        data.update(json.loads(body_unicode))
    except ValueError:
        pass
    return data


###############################################################################
def get_origin(request):
    try:
        origin = request.META['REMOTE_HOST']
    except KeyError:
        origin = 'unknown rest'
    data = get_payload(request)
    if 'origin' in data and data['origin']:
        origin = data['origin']
    return origin


###############################################################################
@csrf_exempt
@require_http_methods(["GET", "POST"])
def HostDetail(request, hostpk=None, hostname=None):
    if request.method == "GET":
        hostid = getReferredHost(hostpk, hostname)
        ans = {'result': 'ok', 'host': HostSerialize(hostid, request)}
    elif request.method == "POST":
        origin = get_origin(request)
        try:
            hostid = getReferredHost(hostpk, hostname)
        except Http404:
            newhost = Host(hostname=hostname, origin=origin)
            newhost.save()
            ans = {'result': 'ok', 'host': HostSerialize(newhost, request)}
        else:
            ans = {'result': 'failed - duplicate'}
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
# /keylist/(keypk, key)/[query]
@require_http_methods(["GET"])
def KeyListRest(request, akeypk=None, akey=None, query=None):
    matches = []
    if akeypk:
        akey = get_object_or_404(AllowedKey, id=akeypk)
    elif akey:
        akey = get_object_or_404(AllowedKey, key=akey)
    if query:
        criteria = query.split('/')
        try:
            qualifiers = parseQualifiers(criteria)
        except HostinfoException as exc:    # pragma: no cover
            return JsonResponse({'error': str(exc)}, status=406)
        matches = getMatches(qualifiers)
    else:
        matches = []
    data = calcKeylistVals(key=akey, from_hostids=matches)
    data['result'] = 'ok'
    return JsonResponse(data)


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
    if keyid:
        keytype = keyid.get_validtype_display()
    else:
        keytype = None

    if request.method == "GET":
        if not keyid:
            kvs = get_list_or_404(KeyValue, hostid=hostid)
        else:
            if keypk:
                kvs = get_list_or_404(KeyValue, hostid=hostid, pk=keypk).select_related('keyid')
            else:
                kvs = get_list_or_404(KeyValue, hostid=hostid, keyid=keyid).select_related('keyid')
        sha = [KeyValueSerialize(k, request) for k in kvs]
        return JsonResponse({'result': result, 'keyvalues': sha})
    elif request.method == "POST":
        origin = get_origin(request)
        if KeyValue.objects.filter(hostid=hostid, keyid=keyid, value=value):
            result = 'duplicate'
        elif KeyValue.objects.filter(hostid=hostid, keyid=keyid):
            if keytype == 'list':
                addKeytoHost(hostid=hostid, keyid=keyid, value=value, appendFlag=True, origin=origin)
                result = 'appended'
            else:
                try:
                    addKeytoHost(hostid=hostid, keyid=keyid, value=value, updateFlag=True, origin=origin)
                    result = 'updated'
                except HostinfoException as exc:    # pragma: no cover
                    result = 'failed %s' % str(exc)
        else:
            result = 'created'
            try:
                addKeytoHost(hostid=hostid, keyid=keyid, value=value, origin=origin)
            except HostinfoException as exc:    # pragma: no cover
                result = 'failed %s' % str(exc)
    elif request.method == "DELETE":
        result = 'deleted'
        if keytype == 'list':
            ha = get_object_or_404(KeyValue, hostid=hostid, keyid=keyid, value=value)
            ha.delete()
        else:
            ha = get_object_or_404(KeyValue, hostid=hostid, keyid=keyid)
            ha.delete()

    kvals = []
    for h in KeyValue.objects.filter(hostid=hostid).select_related('keyid').select_related('hostid'):
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
            result = 'ok'
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
def HostList(request, *args):
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
    keyid = get_object_or_404(KeyValue, id=pk.select_related('keyid'))
    ans = {'result': 'ok', 'keyvalue': KeyValueSerialize(keyid, request)}
    return JsonResponse(ans)


###############################################################################
def HostSerialize(obj, request, **kwargs):
    fields = {'keys': False, 'aliases': False, 'links': False, 'dates': False, 'origin': False}
    if 'keys' in kwargs:
        fields['keys'] = kwargs['keys']
    if 'aliases' in kwargs:
        fields['aliases'] = kwargs['aliases']
    if 'links' in kwargs:
        fields['links'] = kwargs['links']
    if 'dates' in kwargs:
        fields['dates'] = kwargs['dates']
    if 'origin' in kwargs:
        fields['origin'] = kwargs['origin']
    if not kwargs:
        fields = {'keys': ['*'], 'aliases': True, 'links': True, 'dates': True, 'origin': True}

    ans = {
        'id': obj.id,
        'hostname': obj.hostname,
        'url': request.build_absolute_uri(reverse('resthost', args=(obj.id,)))
        }

    if fields['origin']:
        ans['origin'] = obj.origin

    if fields['dates']:
        ans['createdate'] = obj.createdate
        ans['modifieddate'] = obj.modifieddate

    if fields['keys']:
        keys = {}
        for ak in AllowedKey.objects.all():
            if '*' in fields['keys'] or ak.key in fields['keys']:
                keys[ak.id] = ak.key
        keyvals = {}
        for k in KeyValue.objects.filter(hostid=obj).select_related('keyid'):
            try:
                keyname = keys[k.keyid_id]
            except KeyError:
                continue
            if keyname not in keyvals:
                keyvals[keyname] = []
            keyvals[keyname].append(KeyValueShortSerialize(k, request))
        ans['keyvalues'] = keyvals

    if fields['aliases']:
        aliases = []
        for h in HostAlias.objects.filter(hostid=obj):
            aliases.append(HostAliasSerialize(h, request))
        ans['aliases'] = aliases

    if fields['links']:
        links = []
        for l in Links.objects.filter(hostid=obj):
            links.append(LinkSerialize(l, request))
        ans['links'] = links

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
    return HostSerialize(obj, request, keys=False, aliases=False, links=False, dates=False)


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
def KeyValueShortSerialize(obj, request):
    ans = {
        'id': obj.id,
        'url': request.build_absolute_uri(reverse('restkval', args=(obj.id,))),
        'key': obj.keyid.key,
        'value': obj.value,
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
