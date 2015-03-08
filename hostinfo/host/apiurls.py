from django.conf.urls import url, include

import restviews

hostspec = r'((?P<pk>[0-9]+?)|(?P<name>\S+?))'
aliasspec = r'((?P<aliaspk>[0-9]+?)|(?P<alias>\S*?))'

urlpatterns = [
    url(r'', include([
        url(r'host/%s/alias/%s/?$' % (hostspec, aliasspec), restviews.HostAliasRest, name='restalias'),
        url(r'host/%s/?$' % hostspec, restviews.HostDetail, name='resthost'),
        url(r'host/$', restviews.HostList),
        url(r'key/%s' % hostspec, restviews.KeyDetail, name='restkey'),
        url(r'kval/(?P<pk>[0-9]+?)/$', restviews.KValDetail, name='restkval'),
        url(r'query/(?P<query>\S+?)/$', restviews.HostQuery),
        ]
    ))
]
