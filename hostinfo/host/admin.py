#
# Django models definition for hostinfo CMDB
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2008 Dougal Scott
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import admin
from models import Host, HostAlias, AllowedKey, KeyValue, RestrictedValue, UndoLog, Links

class KeyValueInline(admin.TabularInline):
    model=KeyValue

class HostAliasInline(admin.TabularInline):
    model=HostAlias

class LinksInline(admin.TabularInline):
    model=Links

class HostAdmin(admin.ModelAdmin):
    search_fields=['hostname']
    inlines = [ KeyValueInline, HostAliasInline, LinksInline ]

class HostAliasAdmin(admin.ModelAdmin):
    search_fields=['hostid','alias']

class AllowedKeyAdmin(admin.ModelAdmin):
    search_fields=['key']
    list_display=('key', 'validtype', 'restrictedFlag', 'readonlyFlag', 'auditFlag', 'desc')

class KeyValueAdmin(admin.ModelAdmin):
    search_fields=['hostid__hostname', 'keyid__key','value']
    list_display=('hostid', 'keyid','value')
 
class RestrictedValueAdmin(admin.ModelAdmin):
    search_fields=['keyid__key', 'value']
    list_display=('keyid','value')

class LinksAdmin(admin.ModelAdmin):
    list_display=('tag','hostid','url')

class UndoLogAdmin(admin.ModelAdmin):
    list_display=('user','action', 'actiondate')

admin.site.register(Host, HostAdmin)
admin.site.register(HostAlias, HostAliasAdmin)
admin.site.register(AllowedKey, AllowedKeyAdmin)
admin.site.register(KeyValue, KeyValueAdmin)
admin.site.register(RestrictedValue, RestrictedValueAdmin)
admin.site.register(UndoLog, UndoLogAdmin)
admin.site.register(Links, LinksAdmin)

#EOF
