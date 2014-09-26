# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=200)),
                ('validtype', models.IntegerField(default=1, choices=[(1, b'single'), (2, b'list'), (3, b'date')])),
                ('desc', models.CharField(max_length=250, blank=True)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('restrictedFlag', models.BooleanField(default=False)),
                ('readonlyFlag', models.BooleanField(default=False)),
                ('auditFlag', models.BooleanField(default=True)),
                ('reservedFlag1', models.BooleanField(default=True)),
                ('reservedFlag2', models.BooleanField(default=True)),
                ('docpage', models.URLField(null=True, blank=True)),
            ],
            options={
                'ordering': ['key'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AllowedKeyAudit',
            fields=[
                ('key', models.CharField(max_length=200)),
                ('validtype', models.IntegerField(default=1, choices=[(1, b'single'), (2, b'list'), (3, b'date')])),
                ('desc', models.CharField(max_length=250, blank=True)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('restrictedFlag', models.BooleanField(default=False)),
                ('readonlyFlag', models.BooleanField(default=False)),
                ('auditFlag', models.BooleanField(default=True)),
                ('reservedFlag1', models.BooleanField(default=True)),
                ('reservedFlag2', models.BooleanField(default=True)),
                ('docpage', models.URLField(null=True, blank=True)),
                ('user', models.CharField(max_length=20)),
                ('actor', models.CharField(max_length=250)),
                ('_audit_id', models.AutoField(serialize=False, primary_key=True)),
                ('_audit_timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('_audit_change_type', models.CharField(max_length=1)),
                ('id', models.IntegerField(editable=False, db_index=True)),
            ],
            options={
                'ordering': ['-_audit_timestamp'],
                'db_table': 'host_allowedkey_audit',
                'verbose_name_plural': 'allowed key audit trail',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(unique=True, max_length=200)),
                ('origin', models.CharField(max_length=200, blank=True)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('docpage', models.URLField(null=True, blank=True)),
            ],
            options={
                'ordering': ['hostname'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HostAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(unique=True, max_length=200)),
                ('origin', models.CharField(max_length=200, blank=True)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('hostid', models.ForeignKey(to='host.Host')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HostAliasAudit',
            fields=[
                ('alias', models.CharField(max_length=200)),
                ('origin', models.CharField(max_length=200, blank=True)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('user', models.CharField(max_length=20)),
                ('actor', models.CharField(max_length=250)),
                ('_audit_id', models.AutoField(serialize=False, primary_key=True)),
                ('_audit_timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('_audit_change_type', models.CharField(max_length=1)),
                ('id', models.IntegerField(editable=False, db_index=True)),
                ('hostid', models.ForeignKey(to='host.Host')),
            ],
            options={
                'ordering': ['-_audit_timestamp'],
                'db_table': 'host_hostalias_audit',
                'verbose_name_plural': 'host alias audit trail',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HostAudit',
            fields=[
                ('hostname', models.CharField(max_length=200)),
                ('origin', models.CharField(max_length=200, blank=True)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('docpage', models.URLField(null=True, blank=True)),
                ('user', models.CharField(max_length=20)),
                ('actor', models.CharField(max_length=250)),
                ('_audit_id', models.AutoField(serialize=False, primary_key=True)),
                ('_audit_timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('_audit_change_type', models.CharField(max_length=1)),
                ('id', models.IntegerField(editable=False, db_index=True)),
            ],
            options={
                'ordering': ['-_audit_timestamp'],
                'db_table': 'host_host_audit',
                'verbose_name_plural': 'host audit trail',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=200, blank=True)),
                ('origin', models.CharField(max_length=200, blank=True)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('hostid', models.ForeignKey(to='host.Host')),
                ('keyid', models.ForeignKey(to='host.AllowedKey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KeyValueAudit',
            fields=[
                ('value', models.CharField(max_length=200, blank=True)),
                ('origin', models.CharField(max_length=200, blank=True)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('user', models.CharField(max_length=20)),
                ('actor', models.CharField(max_length=250)),
                ('_audit_id', models.AutoField(serialize=False, primary_key=True)),
                ('_audit_timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('_audit_change_type', models.CharField(max_length=1)),
                ('id', models.IntegerField(editable=False, db_index=True)),
                ('hostid', models.ForeignKey(to='host.Host')),
                ('keyid', models.ForeignKey(to='host.AllowedKey')),
            ],
            options={
                'ordering': ['-_audit_timestamp'],
                'db_table': 'host_keyvalue_audit',
                'verbose_name_plural': 'key value audit trail',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Links',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=200)),
                ('tag', models.CharField(max_length=100)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('hostid', models.ForeignKey(to='host.Host')),
            ],
            options={
                'ordering': ['hostid', 'tag'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinksAudit',
            fields=[
                ('url', models.CharField(max_length=200)),
                ('tag', models.CharField(max_length=100)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('user', models.CharField(max_length=20)),
                ('actor', models.CharField(max_length=250)),
                ('_audit_id', models.AutoField(serialize=False, primary_key=True)),
                ('_audit_timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('_audit_change_type', models.CharField(max_length=1)),
                ('id', models.IntegerField(editable=False, db_index=True)),
                ('hostid', models.ForeignKey(to='host.Host')),
            ],
            options={
                'ordering': ['-_audit_timestamp'],
                'db_table': 'host_links_audit',
                'verbose_name_plural': 'links audit trail',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RestrictedValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=200)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('keyid', models.ForeignKey(to='host.AllowedKey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RestrictedValueAudit',
            fields=[
                ('value', models.CharField(max_length=200)),
                ('createdate', models.DateField(auto_now_add=True)),
                ('modifieddate', models.DateField(auto_now=True)),
                ('user', models.CharField(max_length=20)),
                ('actor', models.CharField(max_length=250)),
                ('_audit_id', models.AutoField(serialize=False, primary_key=True)),
                ('_audit_timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('_audit_change_type', models.CharField(max_length=1)),
                ('id', models.IntegerField(editable=False, db_index=True)),
                ('keyid', models.ForeignKey(to='host.AllowedKey')),
            ],
            options={
                'ordering': ['-_audit_timestamp'],
                'db_table': 'host_restrictedvalue_audit',
                'verbose_name_plural': 'restricted value audit trail',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UndoLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=200)),
                ('actiondate', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='restrictedvalue',
            unique_together=set([('keyid', 'value')]),
        ),
        migrations.AlterUniqueTogether(
            name='keyvalue',
            unique_together=set([('hostid', 'keyid', 'value')]),
        ),
    ]
