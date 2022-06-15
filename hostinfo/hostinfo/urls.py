""" URL handler for hostinfo """
from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView

from .views import version

admin.autodiscover()

urlpatterns = [
    path("hostinfo/", include("host.urls")),
    path("mediawiki/", include("host.mediawiki_urls")),
    path("bare/", include("host.bare_urls")),
    path("_version", version),
    path("api/", include("host.api_urls")),
    path("report/", include("report.urls")),
    path("hostinfo-admin/", admin.site.urls),
]

urlpatterns += [
    path(
        "accounts/login/",
        LoginView.as_view(
            template_name="registration/login.html",
        ),
        name="login",
    ),
    path("accounts/logout/", LogoutView.as_view(next_page="/hostinfo/"), name="logoff"),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

# EOF
