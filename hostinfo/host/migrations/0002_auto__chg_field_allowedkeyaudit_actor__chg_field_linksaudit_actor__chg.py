# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'AllowedKeyAudit.actor'
        db.alter_column(u'host_allowedkey_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=250))

        # Changing field 'LinksAudit.actor'
        db.alter_column(u'host_links_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=250))

        # Changing field 'RestrictedValueAudit.actor'
        db.alter_column(u'host_restrictedvalue_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=250))

        # Changing field 'HostAudit.actor'
        db.alter_column(u'host_host_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=250))

        # Changing field 'KeyValueAudit.actor'
        db.alter_column(u'host_keyvalue_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=250))

        # Changing field 'HostAliasAudit.actor'
        db.alter_column(u'host_hostalias_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=250))

    def backwards(self, orm):

        # Changing field 'AllowedKeyAudit.actor'
        db.alter_column(u'host_allowedkey_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'LinksAudit.actor'
        db.alter_column(u'host_links_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'RestrictedValueAudit.actor'
        db.alter_column(u'host_restrictedvalue_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'HostAudit.actor'
        db.alter_column(u'host_host_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'KeyValueAudit.actor'
        db.alter_column(u'host_keyvalue_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'HostAliasAudit.actor'
        db.alter_column(u'host_hostalias_audit', 'actor', self.gf('django.db.models.fields.CharField')(max_length=50))

    models = {
        u'host.allowedkey': {
            'Meta': {'ordering': "['key']", 'object_name': 'AllowedKey'},
            'auditFlag': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'docpage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'readonlyFlag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reservedFlag1': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reservedFlag2': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'restrictedFlag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'validtype': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'host.allowedkeyaudit': {
            'Meta': {'ordering': "['-_audit_timestamp']", 'object_name': 'AllowedKeyAudit', 'db_table': "u'host_allowedkey_audit'"},
            '_audit_change_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            '_audit_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            '_audit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'auditFlag': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'docpage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'readonlyFlag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reservedFlag1': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reservedFlag2': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'restrictedFlag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'validtype': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'host.host': {
            'Meta': {'ordering': "['hostname']", 'object_name': 'Host'},
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'docpage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'host.hostalias': {
            'Meta': {'object_name': 'HostAlias'},
            'alias': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hostid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'host.hostaliasaudit': {
            'Meta': {'ordering': "['-_audit_timestamp']", 'object_name': 'HostAliasAudit', 'db_table': "u'host_hostalias_audit'"},
            '_audit_change_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            '_audit_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            '_audit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hostid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.Host']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'host.hostaudit': {
            'Meta': {'ordering': "['-_audit_timestamp']", 'object_name': 'HostAudit', 'db_table': "u'host_host_audit'"},
            '_audit_change_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            '_audit_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            '_audit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'docpage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'host.keyvalue': {
            'Meta': {'unique_together': "(('hostid', 'keyid', 'value'),)", 'object_name': 'KeyValue'},
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hostid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.AllowedKey']"}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'host.keyvalueaudit': {
            'Meta': {'ordering': "['-_audit_timestamp']", 'object_name': 'KeyValueAudit', 'db_table': "u'host_keyvalue_audit'"},
            '_audit_change_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            '_audit_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            '_audit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hostid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.Host']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'keyid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.AllowedKey']"}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'host.links': {
            'Meta': {'ordering': "['hostid', 'tag']", 'object_name': 'Links'},
            'hostid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'host.linksaudit': {
            'Meta': {'ordering': "['-_audit_timestamp']", 'object_name': 'LinksAudit', 'db_table': "u'host_links_audit'"},
            '_audit_change_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            '_audit_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            '_audit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'hostid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.Host']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'host.restrictedvalue': {
            'Meta': {'unique_together': "(('keyid', 'value'),)", 'object_name': 'RestrictedValue'},
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.AllowedKey']"}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'host.restrictedvalueaudit': {
            'Meta': {'ordering': "['-_audit_timestamp']", 'object_name': 'RestrictedValueAudit', 'db_table': "u'host_restrictedvalue_audit'"},
            '_audit_change_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            '_audit_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            '_audit_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'createdate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'keyid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['host.AllowedKey']"}),
            'modifieddate': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'host.undolog': {
            'Meta': {'object_name': 'UndoLog'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'actiondate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['host']