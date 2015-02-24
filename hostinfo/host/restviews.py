from rest_framework import generics
from .models import Host, AllowedKey, RestrictedValue, Links
from .serializers import HostSerializer, AllowedKeySerializer
from .serializers import RestrictedValueSerializer, LinksSerializer


class HostList(generics.ListCreateAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer


class AllowedKeyList(generics.ListCreateAPIView):
    queryset = AllowedKey.objects.all()
    serializer_class = AllowedKeySerializer


class AllowedKeyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AllowedKey.objects.all()
    serializer_class = AllowedKeySerializer


class LinksList(generics.ListCreateAPIView):
    queryset = Links.objects.all()
    serializer_class = LinksSerializer


class LinksDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Links.objects.all()
    serializer_class = LinksSerializer


class RestrictedValueList(generics.ListCreateAPIView):
    queryset = RestrictedValue.objects.all()
    serializer_class = RestrictedValueSerializer


class RestrictedValueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RestrictedValue.objects.all()
    serializer_class = RestrictedValueSerializer

# EOF
