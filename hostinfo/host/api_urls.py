""" API Url handler """
from django.urls import path

from .rest_views import (
    HostAliasRest,
    HostKeyRest,
    HostLinkRest,
    HostDetail,
    KeyListRest,
)
from .rest_views import HostQuery, HostList, KeyDetail, KValDetail, AliasList

hostspec = "(<int:hostpk>|<str:hostname>)"
aliasspec = "(<int:aliaspk>|<str:alias>)"
kvalspec = "(<int:keypk>|<str:key>)"
akeyspec = "(<int:akeypk>|<str:akey>)"
linkspec = "(<int:linkpk>|<str:tagname>)"

urlpatterns = [
    path("alias/", AliasList),
    path(
        "host/%s/alias/%s/" % (hostspec, aliasspec), HostAliasRest, name="hostaliasrest"
    ),
    path("host/%s/alias/" % hostspec, HostAliasRest, name="hostaliasrest"),
    path(
        "host/%s/key/%s/<str:value>/" % (hostspec, kvalspec),
        HostKeyRest,
        name="hostkeyrest",
    ),
    path("host/%s/key/%s/" % (hostspec, kvalspec), HostKeyRest, name="hostkeyrest"),
    path(
        "host/%s/link/%s/<str:url>" % (hostspec, linkspec),
        HostLinkRest,
        name="hostlinkrest",
    ),
    path("host/%s/link/%s/" % (hostspec, linkspec), HostLinkRest, name="hostlinkrest"),
    path("host/%s/" % hostspec, HostDetail, name="resthost"),
    path("host/", HostList),
    path("key/%s" % akeyspec, KeyDetail, name="restakey"),
    path("kval/<int:pk>/", KValDetail, name="restkval"),
    path("query/<str:query>/", HostQuery),
    path("keylist/%s/<str:query>" % akeyspec, KeyListRest),
]

# EOF
