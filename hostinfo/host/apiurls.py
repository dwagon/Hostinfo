from django.conf.urls import url, include

import restviews

urlpatterns = [
    url(r'', include([
        url(r'host/((?P<pk>[0-9]+)|(?P<name>\S+))/$', restviews.HostDetail, name='resthost'),
        url(r'host/$', restviews.HostList),
        url(r'key/((?P<pk>[0-9]+)|(?P<name>\S+))/$', restviews.KeyDetail, name='restkey'),
        url(r'alias/((?P<pk>[0-9]+)|(?P<name>\S+))/$', restviews.AliasDetail, name='restalias'),
        url(r'kval/(?P<pk>[0-9]+)/$', restviews.KValDetail, name='restkval'),
        url(r'query/(?P<query>\S+)/$', restviews.HostQuery),
        ]
    ))
]
