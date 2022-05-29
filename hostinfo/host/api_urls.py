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
        f"host/{hostspec}/alias/{aliasspec}/", HostAliasRest, name="hostaliasrest"
    ),
    path(f"host/{hostspec}/alias/", HostAliasRest, name="hostaliasrest"),
    path(
        f"host/{hostspec}/key/{kvalspec}/<str:value>/",
        HostKeyRest,
        name="hostkeyrest",
    ),
    path(f"host/{hostspec}/key/{kvalspec}/", HostKeyRest, name="hostkeyrest"),
    path(
        f"host/{hostspec}/link/{linkspec}/<str:url>",
        HostLinkRest,
        name="hostlinkrest",
    ),
    path(f"host/{hostspec}/link/{linkspec}/", HostLinkRest, name="hostlinkrest"),
    path(f"host/{hostspec}/", HostDetail, name="resthost"),
    path("host/", HostList),
    path(f"key/{akeyspec}", KeyDetail, name="restakey"),
    path("kval/<int:pk>/", KValDetail, name="restkval"),
    path("query/<str:query>/", HostQuery),
    path(f"keylist/{akeyspec}/<str:query>", KeyListRest),
]

# EOF
