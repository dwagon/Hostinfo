from django.conf.urls import url

from .rest_views import HostAliasRest, HostKeyRest, HostLinkRest, HostDetail
from .rest_views import KeyListRest, KeyList, HostRename
from .rest_views import HostQuery, HostList, KeyDetail, KValDetail, AliasList
from .rest_views import RestrictedValueRest

hostnamespec = '(?P<hostname>\S+?)'
hostspec = r'((?P<hostpk>[0-9]+?)|{})'.format(hostnamespec)
aliasspec = r'((?P<aliaspk>[0-9]+?)|(?P<alias>\S*?))'
kvalspec = r'((?P<keypk>[0-9]+?)|(?P<key>\S*?))'
akeyspec = r'((?P<akeypk>[0-9]+?)|(?P<akey>[a-z_\-0-9]+?))'
linkspec = r'((?P<linkpk>[0-9]+?)|(?P<tagname>\S*?))'

urlpatterns = [
    url(r'^alias/?$', AliasList),
    url(r'^host/{}/hostname/(?P<newname>\S+?)/?$'.format(hostspec, hostnamespec), HostRename),
    url(r'^host/{}/alias/{}/?$'.format(hostspec, aliasspec), HostAliasRest, name='hostaliasrest'),
    url(r'^host/{}/alias/?$'.format(hostspec), HostAliasRest, name='hostaliasrest'),
    url(r'^host/{}/key/{}/(?P<value>.*)/?$'.format(hostspec, kvalspec), HostKeyRest, name='hostkeyrest'),
    url(r'^host/{}/key/{}/?$'.format(hostspec, kvalspec), HostKeyRest, name='hostkeyrest'),
    url(r'^host/{}/link/{}/(?P<url>.*)/?$'.format(hostspec, linkspec), HostLinkRest, name='hostlinkrest'),
    url(r'^host/{}/link/{}/?$'.format(hostspec, linkspec), HostLinkRest, name='hostlinkrest'),
    url(r'^host/{}/?$'.format(hostspec), HostDetail, name='resthost'),
    url(r'^host/?$', HostList),
    url(r'^key/{}/?$'.format(akeyspec), KeyDetail, name='restakey'),
    url(r'^key/?$', KeyList),
    url(r'^rval/{}/?$'.format(akeyspec), RestrictedValueRest),
    url(r'^rval/{}/(?P<val>\S+?)/?$'.format(akeyspec), RestrictedValueRest),
    url(r'^kval/(?P<pk>[0-9]+?)/?$', KValDetail, name='restkval'),
    url(r'^query/(?P<query>\S+?)/?$', HostQuery),
    url(r'^keylist/{}/(?P<query>\S+?)?/?$'.format(akeyspec), KeyListRest),
]

# EOF
