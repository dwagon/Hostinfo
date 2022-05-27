""" URL handler for hostinfo """
from django.urls import include, path
# from django.contrib.auth.views import login, logout
from django.conf import settings
from django.contrib import admin

from .views import version

admin.autodiscover()

urlpatterns = [
    path(r'^hostinfo/', include('host.urls')),
    path(r'^mediawiki/', include('host.mediawiki_urls')),
    path(r'^bare/', include('host.bare_urls')),
    path(r'^_version', version),
    path(r'^api(/v1)?/', include('host.api_urls')),
    path(r'^report/', include('report.urls')),
    path(r'^hostinfo-admin/', include(admin.site.urls)),
]

# urlpatterns += [
#     path(r'^accounts/login/', login, {'template_name': 'registration/login.html'}, name='login'),
#     path(r'^accounts/logout/', logout, {'next_page': '/hostinfo/'}, name='logoff'),
# ]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    urlpatterns += [
        path(r'^__debug__/', include(debug_toolbar.urls)),
    ]

# EOF
