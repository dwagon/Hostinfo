from .models import Host, AllowedKey, KeyValue, HostAlias, Links
from .models import RestrictedValue, RestrictedValueException
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
    aliases = HostAlias.objects.all()
    ans = {'result': 'ok', 'status': '200', 'aliases': [HostAliasSerialize(a, request) for a in aliases.select_related('hostid')]}
    return JsonResponse(ans)


###############################################################################
def getSerializerArgs(request):
    sargs = {'keys': ['*'], 'links': False, 'aliases': False, 'dates': False, 'origin': False}
    payload = get_payload(request)
    if 'keys' in payload:
        sargs['keys'] = payload['keys']
    if 'origin' in payload:
        sargs['origin'] = payload['origin']
    # Backward compatible options
    if 'links' in payload:
        sargs['show_links'] = True
    if 'aliases' in payload:
        sargs['show_aliases'] = True
    if 'dates' in payload:
        sargs['show_dates'] = True
    if 'host' in payload:
        sargs['show_host'] = True
    # Backward compatible options

    # Less ambiguous options
    if 'show_links' in payload:
        sargs['show_links'] = True
    if 'hide_links' in payload:
        sargs['show_links'] = False
    if 'show_dates' in payload:
        sargs['show_dates'] = True
    if 'hide_dates' in payload:
        sargs['show_dates'] = False
    if 'show_origin' in payload:
        sargs['show_origin'] = True
    if 'hide_origin' in payload:
        sargs['show_origin'] = False
    if 'show_url' in payload:
        sargs['show_url'] = True
    if 'hide_url' in payload:
        sargs['show_url'] = False

    return sargs


###############################################################################
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def RestrictedValueRest(request, akeypk=None, akey=None, val=None):
    if akeypk:
        akey = get_object_or_404(AllowedKey, id=akeypk)
    elif akey:
        akey = get_object_or_404(AllowedKey, key=akey)
    if request.method == "GET":
        rlist = RestrictedValue.objects.filter(keyid=akey)
        ans = {'result': 'ok', 'restricted': [RestrictedValueSerialize(r, request) for r in rlist]}
    elif request.method == "POST":
        rval = RestrictedValue(keyid=akey, value=val)
        rval.save()
        ans = {'result': 'ok'}
    elif request.method == "DELETE":
        rval = RestrictedValue.objects.get(keyid=akey, value=val)
        rval.delete()
        ans = {'result': 'ok'}
    return JsonResponse(ans)


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
    hosts = Host.objects.filter(pk__in=matches)
    ans = {
        'result': '%d matching hosts' % len(hosts),
        'status': '200',
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

    for k, v in data.items():
        if hasattr(v, 'len') and len(v) == 1:
            data[k] = v[0]
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
@require_http_methods(["GET", "POST", "DELETE"])
def HostDetail(request, hostpk=None, hostname=None):
    sargs = getSerializerArgs(request)
    if request.method == "GET":
        hostid = getReferredHost(hostpk, hostname)
        ans = {'result': 'ok', 'host': HostSerialize(hostid, request, **sargs)}
    elif request.method == "POST":
        origin = get_origin(request)
        try:
            hostid = getReferredHost(hostpk, hostname)
        except Http404:
            newhost = Host(hostname=hostname, origin=origin)
            newhost.save()
            ans = {'result': 'ok', 'status': '200', 'host': HostSerialize(newhost, request)}
        else:
            ans = {'result': 'failed - duplicate', 'status': '401'}
    elif request.method == "DELETE":
        hostid = getReferredHost(hostpk, hostname)

        # Delete aliases
        aliases = HostAlias.objects.filter(hostid=hostid)
        for alias in aliases:
            alias.delete()

        # Delete key/values
        kvs = KeyValue.objects.filter(hostid=hostid)
        for kv in kvs:
            kv.delete(readonlychange=True)

        # Delete the host
        hostid.delete()
        ans = {'result': 'ok', 'status': '200'}
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
            return JsonResponse({'error': str(exc)}, status='406')
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
    hostid = getReferredHost(hostpk, hostname)
    ans = {}
    error = ''
    keyid = None

    # Get the id of the AllowedKey
    try:
        if keypk:
            ko = get_object_or_404(KeyValue, pk=keypk)
            keyid = ko.keyid
        if key:
            keyid = get_object_or_404(AllowedKey, key=key)
    except Http404:
        ans['result'] = 'Failed'
        ans['error'] = 'Key {} not found'.format(key)
        ans['status'] = '404'
        return JsonResponse(ans)

    sargs = getSerializerArgs(request)

    if request.method == "GET":
        return hostKeyGet(request, hostid, keyid)
    elif request.method == "POST":
        result, status, error = hostKeyPost(request, hostid, keyid, value)
    elif request.method == "DELETE":
        result, status = hostKeyDelete(request, hostid, keyid, value)

    ans['result'] = result
    ans['status'] = status
    if error:
        ans['error'] = error

    kvals = []
    for h in KeyValue.objects.filter(hostid=hostid).select_related('keyid').select_related('hostid'):
        kvals.append(KeyValueSerialize(h, request, **sargs))
    ans['keyvalues'] = kvals
    return JsonResponse(ans)


###############################################################################
def hostKeyGet(request, hostid, keyid):
    result = 'ok'
    if not keyid:
        kvs = get_list_or_404(KeyValue, hostid=hostid)
    else:
        kvs = get_list_or_404(KeyValue, hostid=hostid, keyid=keyid)
    sha = [KeyValueSerialize(k, request) for k in kvs]
    return JsonResponse({'result': result, 'keyvalues': sha})


###############################################################################
def hostKeyDelete(request, hostid, keyid, value):
    result = 'deleted'
    status = '200'
    if keyid:
        keytype = keyid.get_validtype_display()
    else:
        keytype = None
    if keytype == 'list':
        ha = get_object_or_404(KeyValue, hostid=hostid, keyid=keyid, value=value)
        ha.delete()
    else:
        ha = get_object_or_404(KeyValue, hostid=hostid, keyid=keyid)
        ha.delete()
    return result, status


###############################################################################
def hostKeyPost(request, hostid, keyid, value):
    error = ''
    if keyid:
        keytype = keyid.get_validtype_display()
    else:
        keytype = None
    origin = get_origin(request)
    if KeyValue.objects.filter(hostid=hostid, keyid=keyid, value=value):
        result = 'duplicate'
        status = '201'
    elif KeyValue.objects.filter(hostid=hostid, keyid=keyid):
        if keytype == 'list':
            addKeytoHost(hostid=hostid, keyid=keyid, value=value, appendFlag=True, origin=origin)
            result = 'appended'
            status = '202'
        else:
            try:
                addKeytoHost(hostid=hostid, keyid=keyid, value=value, updateFlag=True, origin=origin)
                result = 'updated'
                status = '203'
            except RestrictedValueException as exc:
                result = 'failed %s' % str(exc)
                error = str(exc)
                status = '402'
            except HostinfoException as exc:    # pragma: no cover
                result = 'failed %s' % str(exc)
                error = str(exc)
                status = '400'
    else:
        result = 'created'
        status = '200'
        try:
            addKeytoHost(hostid=hostid, keyid=keyid, value=value, origin=origin)
        except HostinfoException as exc:    # pragma: no cover
            result = 'failed %s' % str(exc)
            status = '400'
    return result, status, error


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
# /key/
@require_http_methods(["GET"])
def KeyList(request, *args):
    """ Return all keys """
    allkeys = AllowedKey.objects.all()
    ans = {'result': 'ok', 'keys': []}
    for key in allkeys:
        ans['keys'].append(AllowedKeySerialize(key, request))
    return JsonResponse(ans)


###############################################################################
# /key/<key>/
@csrf_exempt
@require_http_methods(["GET", "POST"])
def KeyDetail(request, akeypk=None, akey=None):
    if request.method == "GET":
        if akeypk:
            keyid = get_object_or_404(AllowedKey, id=akeypk)
        elif akey:
            keyid = get_object_or_404(AllowedKey, key=akey)
        ans = {'result': 'ok', 'key': AllowedKeySerialize(keyid, request)}
    elif request.method == "POST":
        ans = addKey(request, akey)
    return JsonResponse(ans)


###############################################################################
def determineTruth(payload, key, default=False):
    if key not in payload:
        return default
    pv = payload[key]
    if hasattr(pv, 'strip'):
        pv = pv.strip()
    if hasattr(pv, 'lower'):
        pv = pv.lower()
    if pv in ('true', 'yes', 'on', True):
        return True
    if pv in ('false', 'no', 'off', False):
        return False
    return default


###############################################################################
def addKey(request, akey):
    params = {
        'desc': 'Undescribed',
        'keytype': 'single',
    }
    payload = get_payload(request)
    params['numeric'] = determineTruth(payload, 'numeric', False)
    params['restricted'] = determineTruth(payload, 'restricted', False)
    params['readonly'] = determineTruth(payload, 'readonly', False)
    params['audit'] = determineTruth(payload, 'audit', True)
    if 'desc' in payload:
        params['desc'] = payload['desc']
    if 'keytype' in payload:
        params['keytype'] = payload['keytype']
    try:
        AllowedKey.objects.get(key=akey)
        return {'result': 'failed', 'error': 'Key already exists'}
    except:
        pass
    try:
        newak = AllowedKey(
            key=akey,
            validtype=validateKeytype(params['keytype']),
            desc=params['desc'],
            restrictedFlag=params['restricted'],
            readonlyFlag=params['readonly'],
            numericFlag=params['numeric'],
            auditFlag=params['audit'],
            )
        newak.save()
    except HostinfoException as exc:
        return {'result': 'failed', 'error': str(exc)}

    return {'result': 'ok', 'key': AllowedKeySerialize(newak, request)}


###############################################################################
def validateKeytype(keytype):
    type_choices = [d for k, d in AllowedKey.TYPE_CHOICES]
    vt = -1
    for knum, desc in AllowedKey.TYPE_CHOICES:
        if keytype == desc:
            vt = knum
            break
    if vt < 0:
        raise HostinfoException(
            "Unknown type %s - should be one of %s" % (keytype, ",".join(type_choices)))
    return vt


###############################################################################
@require_http_methods(["GET"])
def KValDetail(request, pk=None):
    sargs = getSerializerArgs(request)
    sargs['show_host'] = True
    keyid = get_object_or_404(KeyValue, id=pk)
    ans = {'result': 'ok', 'keyvalue': KeyValueSerialize(keyid, request, **sargs)}
    return JsonResponse(ans)


###############################################################################
def HostSerialize(obj, request, **kwargs):
    ans = {
        'id': obj.id,
        'hostname': obj.hostname,
        'url': request.build_absolute_uri(reverse('resthost', args=(obj.id,)))
        }

    if kwargs.get('show_origin', False):
        ans['origin'] = obj.origin

    if kwargs.get('show_dates', False):
        ans['createdate'] = obj.createdate
        ans['modifieddate'] = obj.modifieddate

    print_keys = []
    if 'keys' not in kwargs:
        print_keys.append('*')
    else:
        print_keys.extend(kwargs['keys'])
    keys = {}
    for ak in AllowedKey.objects.all():
        if '*' in print_keys or ak.key in print_keys:
            keys[ak.id] = ak.key
    keyvals = {}
    for k in KeyValue.objects.filter(hostid=obj).select_related('keyid'):
        try:
            keyname = keys[k.keyid_id]
        except KeyError:
            continue
        if keyname not in keyvals:
            keyvals[keyname] = []
        keyvals[keyname].append(KeyValueSerialize(k, request, **kwargs))
    ans['keyvalues'] = keyvals

    if kwargs.get('aliases', False):
        aliases = []
        for h in HostAlias.objects.filter(hostid=obj):
            aliases.append(HostAliasSerialize(h, request))
        ans['aliases'] = aliases

    if kwargs.get('links', False):
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
        'numeric': obj.numericFlag,
        'readonly': obj.readonlyFlag,
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
    return HostSerialize(obj, request, keys=[], aliases=False, links=False, dates=False)


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
def KeyValueSerialize(obj, request, **kwargs):
    ans = {
        'id': obj.id,
        'keyid': obj.keyid.id,
        'key': obj.keyid.key,
        'value': obj.value
    }

    if kwargs.get('show_url', False):
        ans['url'] = request.build_absolute_uri(reverse('restkval', args=(obj.id,)))
    if kwargs.get('show_host', False):
        ans['host'] = HostShortSerialize(obj.hostid, request)
    if kwargs.get('show_dates', False):
        ans['createdate'] = obj.createdate
        ans['modifieddate'] = obj.modifieddate
    if kwargs.get('show_origin', False):
        ans['origin'] = obj.origin

    return ans


###############################################################################
def HostAliasSerialize(obj, request, **kwargs):
    ans = {
        'id': obj.id,
        'alias': obj.alias,
        'host': obj.hostid.hostname
        }
    if kwargs.get('show_url', False):
        ans['url'] = request.build_absolute_uri(reverse('hostaliasrest', args=(obj.hostid.hostname, obj.id,))),
    if kwargs.get('show_dates', False):
        ans['createdate'] = obj.createdate
        ans['modifieddate'] = obj.modifieddate
    if kwargs.get('show_origin', False):
        ans['origin'] = obj.origin
    return ans

# EOF
