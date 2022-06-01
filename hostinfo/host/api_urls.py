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

hostspec = r'((?P<hostpk>[0-9]+?)|(?P<hostname>\S+?))'
aliasspec = r'((?P<aliaspk>[0-9]+?)|(?P<alias>\S*?))'
kvalspec = r'((?P<keypk>[0-9]+?)|(?P<key>\S*?))'
akeyspec = r'((?P<akeypk>[0-9]+?)|(?P<akey>\S*?))'
linkspec = r'((?P<linkpk>[0-9]+?)|(?P<tagname>\S*?))'

urlpatterns = [
    path("alias/", AliasList),
    re_path(f"host/{hostspec}/alias/{aliasspec}/$", HostAliasRest, name='hostaliasrest'),
    re_path(f"host/{hostspec}/alias/$", HostAliasRest, name="hostaliasrest"),
    re_path(
        rf"host/{hostspec}/key/{kvalspec}/(?P<value>[^/]+)/$",
        HostKeyRest,
        name="hostkeyrest",
    ),
    re_path(f"host/{hostspec}/key/{kvalspec}/", HostKeyRest, name="hostkeyrest"),
    re_path(f"host/{hostspec}/key/", HostKeyRest, name="hostkeyrest"),
    re_path(
        f"host/{hostspec}/link/{linkspec}/(?P<url>.*)/$",
        HostLinkRest,
        name="hostlinkrest",
    ),
    re_path(f"host/{hostspec}/link/{linkspec}/$", HostLinkRest, name="hostlinkrest"),
    re_path(f"host/{hostspec}/link/$", HostLinkRest, name="hostlinkrest"),
    path("host/<int:hostpk>/", HostDetail, name="resthost"),
    path("host/<str:hostname>/", HostDetail, name="resthost"),
    path("host/", HostList),

    re_path(f"key/{akeyspec}/$", KeyDetail, name="restakey"),
    path("kval/<int:pk>/", KValDetail, name="restkval"),
    re_path(r"query/(?P<query>\S+?)/$", HostQuery),
    re_path(rf"keylist/{akeyspec}/(?P<query>\S+?/)?$", KeyListRest),
]

# EOF
