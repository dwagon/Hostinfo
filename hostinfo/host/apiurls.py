from django.conf.urls import url, include

import restviews

hostspec = r'((?P<hostpk>[0-9]+?)|(?P<hostname>\S+?))'
aliasspec = r'((?P<aliaspk>[0-9]+?)|(?P<alias>\S*?))'
kvalspec = r'((?P<keypk>[0-9]+?)|(?P<key>\S*?))'

# /host/(hostname|pk)/key/(keyname|pk)[/value]

urlpatterns = [
    url(r'', include([
        url(r'host/%s/alias/%s/?$' % (hostspec, aliasspec), restviews.HostAliasRest, name='hostaliasrest'),
        url(r'host/%s/alias/?$' % hostspec, restviews.HostAliasRest, name='hostaliasrest'),
        url(r'host/%s/key/%s/(?P<value>.*)/?$' % (hostspec, kvalspec), restviews.HostKeyRest, name='hostkeyrest'),
        url(r'host/%s/key/%s/?$' % (hostspec, kvalspec), restviews.HostKeyRest, name='hostkeyrest'),
        url(r'host/%s/?$' % hostspec, restviews.HostDetail, name='resthost'),
        url(r'host/$', restviews.HostList),
        url(r'key/%s' % hostspec, restviews.KeyDetail, name='restkey'),
        url(r'kval/(?P<pk>[0-9]+?)/$', restviews.KValDetail, name='restkval'),
        url(r'query/(?P<query>\S+?)/$', restviews.HostQuery),
        ]
    ))
]
