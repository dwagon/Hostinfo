from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

import restviews

urlpatterns = [
    url(r'', include([
        url(r'host/$', restviews.HostList.as_view()),
        url(r'host/(?P<pk>[0-9]+)/$', restviews.HostDetail.as_view()),
        url(r'akey/$', restviews.AllowedKeyList.as_view()),
        url(r'akey/(?P<pk>[0-9]+)/$', restviews.AllowedKeyDetail.as_view()),
        url(r'links/$', restviews.LinksList.as_view()),
        url(r'links/(?P<pk>[0-9]+)/$', restviews.LinksDetail.as_view()),
        url(r'rval/$', restviews.RestrictedValueList.as_view()),
        url(r'rval/(?P<pk>[0-9]+)/$', restviews.RestrictedValueDetail.as_view()),
        ]
    ))
]

urlpatterns = format_suffix_patterns(urlpatterns)
