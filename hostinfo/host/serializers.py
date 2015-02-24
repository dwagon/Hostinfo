from .models import HostAlias, AllowedKey, KeyValue, RestrictedValue, Links
from rest_framework import serializers


class HostSerializer(serializers.Serializer):

    def to_representation(self, obj):
        keys = {}
        for ak in AllowedKey.objects.all():
            keys[ak.id] = ak.key
        keyvals = {}
        for k in KeyValue.objects.filter(hostid=obj):
            keyname = keys[k.keyid_id]
            if keyname not in keyvals:
                keyvals[keyname] = []
            keyvals[keyname].append(k.value)

        aliases = [h.alias for h in HostAlias.objects.filter(hostid=obj)]
        links = [(l.tag, l.url) for l in Links.objects.filter(hostid=obj)]

        ans = {
            'name': obj.hostname,
            'origin': obj.origin,
            'createdate': obj.createdate,
            'modifieddate': obj.modifieddate,
            'keyvalues': keyvals,
            'aliases': aliases,
            'links': links,
            }
        return ans


class AllowedKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedKey


class RestrictedValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestrictedValue


class LinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Links

# EOF
