from django.conf.urls import url, include

from .rest_views import HostAliasRest, HostKeyRest, HostLinkRest, HostDetail, KeyListRest
from .rest_views import HostQuery, HostList, KeyDetail, KValDetail, AliasList

hostspec = r'((?P<hostpk>[0-9]+?)|(?P<hostname>\S+?))'
aliasspec = r'((?P<aliaspk>[0-9]+?)|(?P<alias>\S*?))'
kvalspec = r'((?P<keypk>[0-9]+?)|(?P<key>\S*?))'
akeyspec = r'((?P<akeypk>[0-9]+?)|(?P<akey>\S*?))'
linkspec = r'((?P<linkpk>[0-9]+?)|(?P<tagname>\S*?))'

urlpatterns = [
    url(r'', include([
        url(r'^host/%s/alias/%s/?$' % (hostspec, aliasspec), HostAliasRest, name='hostaliasrest'),
        url(r'^host/%s/alias/?$' % hostspec, HostAliasRest, name='hostaliasrest'),
        url(r'^host/%s/key/%s/(?P<value>.*)/?$' % (hostspec, kvalspec), HostKeyRest, name='hostkeyrest'),
        url(r'^host/%s/key/%s/?$' % (hostspec, kvalspec), HostKeyRest, name='hostkeyrest'),
        url(r'^host/%s/link/%s/(?P<url>.*)/?$' % (hostspec, linkspec), HostLinkRest, name='hostlinkrest'),
        url(r'^host/%s/link/%s/?$' % (hostspec, linkspec), HostLinkRest, name='hostlinkrest'),
        url(r'^host/%s/?$' % hostspec, HostDetail, name='resthost'),
        url(r'^host/$', HostList),
        url(r'^key/%s/?$' % akeyspec, KeyDetail, name='restakey'),
        url(r'^kval/(?P<pk>[0-9]+?)/$', KValDetail, name='restkval'),
        url(r'^query/(?P<query>\S+?)/$', HostQuery),
        url(r'^keylist/%s/(?P<query>\S+?)?/?$' % akeyspec, KeyListRest),
        url(r'^alias/$', AliasList),
        ]
    ))
]

# EOF
