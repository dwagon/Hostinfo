""" API Url handler """
from django.urls import path, re_path

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
    re_path(
        f"host/{hostspec}/alias/{aliasspec}/", HostAliasRest, name="hostaliasrest"
    ),
    re_path(f"host/{hostspec}/alias/", HostAliasRest, name="hostaliasrest"),
    re_path(
        f"host/{hostspec}/key/{kvalspec}/<str:value>/",
        HostKeyRest,
        name="hostkeyrest",
    ),
    re_path(f"host/{hostspec}/key/{kvalspec}/", HostKeyRest, name="hostkeyrest"),
    re_path(
        f"host/{hostspec}/link/{linkspec}/<str:url>",
        HostLinkRest,
        name="hostlinkrest",
    ),
    re_path(f"host/{hostspec}/link/{linkspec}/", HostLinkRest, name="hostlinkrest"),
    path("host/<int:hostpk>/", HostDetail, name="resthost"),
    path("host/<str:hostname>/", HostDetail, name="resthost"),
    path("host/", HostList),
    path("key/<int:akeypk>", KeyDetail, name="restakey"),
    path("key/<str:akey>", KeyDetail, name="restakey"),
    path("kval/<int:pk>/", KValDetail, name="restkval"),
    path("query/<str:query>/", HostQuery),
    path("keylist/<int:akeypk>/<str:query>", KeyListRest),
    path("keylist/<str:akey>/<str:query>", KeyListRest),
]

# EOF
