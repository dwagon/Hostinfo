#
# Django models definition for hostinfo CMDB
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
from django.contrib import admin
from .models import Host, HostAlias, AllowedKey, KeyValue, RestrictedValue, UndoLog, Links
from simple_history.admin import SimpleHistoryAdmin


class KeyValueInline(admin.TabularInline):
    model = KeyValue


class HostAliasInline(admin.TabularInline):
    model = HostAlias


class LinksInline(admin.TabularInline):
    model = Links


class HostAdmin(SimpleHistoryAdmin):
    search_fields = ['hostname']
    inlines = [KeyValueInline, HostAliasInline, LinksInline]


class HostAliasAdmin(SimpleHistoryAdmin):
    search_fields = ['hostid', 'alias']


class AllowedKeyAdmin(SimpleHistoryAdmin):
    search_fields = ['key']
    list_display = (
        'key', 'validtype', 'restrictedFlag', 'readonlyFlag', 'auditFlag', 'desc')


class KeyValueAdmin(SimpleHistoryAdmin):
    search_fields = ['hostid__hostname', 'keyid__key', 'value']
    list_display = ('hostid', 'keyid', 'value')


class RestrictedValueAdmin(SimpleHistoryAdmin):
    search_fields = ['keyid__key', 'value']
    list_display = ('keyid', 'value')


class LinksAdmin(SimpleHistoryAdmin):
    list_display = ('tag', 'hostid', 'url')


class UndoLogAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'action', 'actiondate')

admin.site.register(Host, HostAdmin)
admin.site.register(HostAlias, HostAliasAdmin)
admin.site.register(AllowedKey, AllowedKeyAdmin)
admin.site.register(KeyValue, KeyValueAdmin)
admin.site.register(RestrictedValue, RestrictedValueAdmin)
admin.site.register(UndoLog, UndoLogAdmin)
admin.site.register(Links, LinksAdmin)

# EOF
