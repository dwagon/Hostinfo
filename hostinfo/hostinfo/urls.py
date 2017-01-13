from django.conf.urls import include, url
from django.contrib.auth.views import login, logout
from django.conf import settings
from django.contrib import admin

from .views import version

admin.autodiscover()

urlpatterns = [
    url(r'^hostinfo/', include('host.urls')),
    url(r'^mediawiki/', include('host.mediawiki_urls')),
    url(r'^bare/', include('host.bare_urls')),
    url(r'^_version', version),
    url(r'^api(/v1)?/', include('host.api_urls')),
    url(r'^report/', include('report.urls')),
    url(r'^hostinfo-admin/', include(admin.site.urls)),
]

urlpatterns += [
    url(r'^accounts/login/', login, {'template_name': 'registration/login.html'}, name='login'),
    url(r'^accounts/logout/', logout, {'next_page': '/hostinfo/'}, name='logoff'),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

# EOF
