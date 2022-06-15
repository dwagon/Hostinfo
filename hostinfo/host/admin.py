"""Django admin models definition for hostinfo CMDB"""
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Host,
    HostAlias,
    AllowedKey,
    KeyValue,
    RestrictedValue,
    UndoLog,
    Links,
)


class KeyValueInline(admin.TabularInline):
    """ Display KeyValue in-line"""
    model = KeyValue


class HostAliasInline(admin.TabularInline):
    """ Display HostAliases in-line"""
    model = HostAlias


class LinksInline(admin.TabularInline):
    """ Display Links in-line"""
    model = Links


class HostAdmin(SimpleHistoryAdmin):
    """ Admin Class for HostAdmin """
    search_fields = ["hostname"]
    inlines = [KeyValueInline, HostAliasInline, LinksInline]


class HostAliasAdmin(SimpleHistoryAdmin):
    """ Admin Class for HostAlias """
    search_fields = ["hostid", "alias"]


class AllowedKeyAdmin(SimpleHistoryAdmin):
    """ Admin Class for AllowedKey """
    search_fields = ["key"]
    list_display = (
        "key",
        "validtype",
        "restrictedFlag",
        "readonlyFlag",
        "numericFlag",
        "auditFlag",
        "desc",
    )


class KeyValueAdmin(SimpleHistoryAdmin):
    """ Admin Class for KeyValue """
    search_fields = ["hostid__hostname", "keyid__key", "value"]
    list_display = ("hostid", "keyid", "value")


class RestrictedValueAdmin(SimpleHistoryAdmin):
    """ Admin Class for RestrictedValue """
    search_fields = ["keyid__key", "value"]
    list_display = ("keyid", "value")


class LinksAdmin(SimpleHistoryAdmin):
    """ Admin Class for Links """
    list_display = ("tag", "hostid", "url")


class UndoLogAdmin(SimpleHistoryAdmin):
    """ Admin Class for UndoLog """
    list_display = ("user", "action", "actiondate")


admin.site.register(Host, HostAdmin)
admin.site.register(HostAlias, HostAliasAdmin)
admin.site.register(AllowedKey, AllowedKeyAdmin)
admin.site.register(KeyValue, KeyValueAdmin)
admin.site.register(RestrictedValue, RestrictedValueAdmin)
admin.site.register(UndoLog, UndoLogAdmin)
admin.site.register(Links, LinksAdmin)

# EOF
