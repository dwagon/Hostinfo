# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HostAudit'
        db.create_table(u'host_host_audit', (
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('docpage', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('actor', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('_audit_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_audit_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('_audit_change_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'host', ['HostAudit'])

        # Adding model 'Host'
        db.create_table(u'host_host', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('docpage', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'host', ['Host'])

        # Adding model 'HostAliasAudit'
        db.create_table(u'host_hostalias_audit', (
            ('hostid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.Host'])),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('actor', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('_audit_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_audit_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('_audit_change_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'host', ['HostAliasAudit'])

        # Adding model 'HostAlias'
        db.create_table(u'host_hostalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.Host'])),
            ('alias', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'host', ['HostAlias'])

        # Adding model 'AllowedKeyAudit'
        db.create_table(u'host_allowedkey_audit', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('validtype', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('restrictedFlag', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('readonlyFlag', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('auditFlag', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('reservedFlag1', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('reservedFlag2', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('docpage', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('actor', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('_audit_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_audit_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('_audit_change_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'host', ['AllowedKeyAudit'])

        # Adding model 'AllowedKey'
        db.create_table(u'host_allowedkey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('validtype', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('restrictedFlag', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('readonlyFlag', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('auditFlag', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('reservedFlag1', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('reservedFlag2', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('docpage', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'host', ['AllowedKey'])

        # Adding model 'KeyValueAudit'
        db.create_table(u'host_keyvalue_audit', (
            ('hostid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.Host'])),
            ('keyid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.AllowedKey'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('actor', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('_audit_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_audit_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('_audit_change_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'host', ['KeyValueAudit'])

        # Adding model 'KeyValue'
        db.create_table(u'host_keyvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.Host'])),
            ('keyid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.AllowedKey'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'host', ['KeyValue'])

        # Adding unique constraint on 'KeyValue', fields ['hostid', 'keyid', 'value']
        db.create_unique(u'host_keyvalue', ['hostid_id', 'keyid_id', 'value'])

        # Adding model 'UndoLog'
        db.create_table(u'host_undolog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('actiondate', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'host', ['UndoLog'])

        # Adding model 'RestrictedValueAudit'
        db.create_table(u'host_restrictedvalue_audit', (
            ('keyid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.AllowedKey'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('actor', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('_audit_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_audit_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('_audit_change_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'host', ['RestrictedValueAudit'])

        # Adding model 'RestrictedValue'
        db.create_table(u'host_restrictedvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keyid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.AllowedKey'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('createdate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'host', ['RestrictedValue'])

        # Adding unique constraint on 'RestrictedValue', fields ['keyid', 'value']
        db.create_unique(u'host_restrictedvalue', ['keyid_id', 'value'])

        # Adding model 'LinksAudit'
        db.create_table(u'host_links_audit', (
            ('hostid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.Host'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('actor', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('_audit_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_audit_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('_audit_change_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'host', ['LinksAudit'])

        # Adding model 'Links'
        db.create_table(u'host_links', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['host.Host'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('modifieddate', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'host', ['Links'])


    def backwards(self, orm):
        # Removing unique constraint on 'RestrictedValue', fields ['keyid', 'value']
        db.delete_unique(u'host_restrictedvalue', ['keyid_id', 'value'])

        # Removing unique constraint on 'KeyValue', fields ['hostid', 'keyid', 'value']
        db.delete_unique(u'host_keyvalue', ['hostid_id', 'keyid_id', 'value'])

        # Deleting model 'HostAudit'
        db.delete_table(u'host_host_audit')

        # Deleting model 'Host'
        db.delete_table(u'host_host')

        # Deleting model 'HostAliasAudit'
        db.delete_table(u'host_hostalias_audit')

        # Deleting model 'HostAlias'
        db.delete_table(u'host_hostalias')

        # Deleting model 'AllowedKeyAudit'
        db.delete_table(u'host_allowedkey_audit')

        # Deleting model 'AllowedKey'
        db.delete_table(u'host_allowedkey')

        # Deleting model 'KeyValueAudit'
        db.delete_table(u'host_keyvalue_audit')

        # Deleting model 'KeyValue'
        db.delete_table(u'host_keyvalue')

        # Deleting model 'UndoLog'
        db.delete_table(u'host_undolog')

        # Deleting model 'RestrictedValueAudit'
        db.delete_table(u'host_restrictedvalue_audit')

        # Deleting model 'RestrictedValue'
        db.delete_table(u'host_restrictedvalue')

        # Deleting model 'LinksAudit'
        db.delete_table(u'host_links_audit')

        # Deleting model 'Links'
        db.delete_table(u'host_links')


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
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'actor': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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