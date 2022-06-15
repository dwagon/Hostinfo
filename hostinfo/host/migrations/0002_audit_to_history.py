# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("host", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalAllowedKey",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                ("key", models.CharField(max_length=200)),
                (
                    "validtype",
                    models.IntegerField(
                        default=1, choices=[(1, b"single"), (2, b"list"), (3, b"date")]
                    ),
                ),
                ("desc", models.CharField(max_length=250, blank=True)),
                ("createdate", models.DateField(editable=False, blank=True)),
                ("modifieddate", models.DateField(editable=False, blank=True)),
                ("restrictedFlag", models.BooleanField(default=False)),
                ("readonlyFlag", models.BooleanField(default=False)),
                ("auditFlag", models.BooleanField(default=True)),
                ("reservedFlag1", models.BooleanField(default=True)),
                ("reservedFlag2", models.BooleanField(default=True)),
                ("docpage", models.URLField(null=True, blank=True)),
                ("history_id", models.AutoField(serialize=False, primary_key=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        max_length=1,
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical allowed key",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="HistoricalHost",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                ("hostname", models.CharField(max_length=200, db_index=True)),
                ("origin", models.CharField(max_length=200, blank=True)),
                ("createdate", models.DateField(editable=False, blank=True)),
                ("modifieddate", models.DateField(editable=False, blank=True)),
                ("docpage", models.URLField(null=True, blank=True)),
                ("history_id", models.AutoField(serialize=False, primary_key=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        max_length=1,
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical host",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="HistoricalHostAlias",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                (
                    "hostid_id",
                    models.IntegerField(db_index=True, null=True, blank=True),
                ),
                ("alias", models.CharField(max_length=200, db_index=True)),
                ("origin", models.CharField(max_length=200, blank=True)),
                ("createdate", models.DateField(editable=False, blank=True)),
                ("modifieddate", models.DateField(editable=False, blank=True)),
                ("history_id", models.AutoField(serialize=False, primary_key=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        max_length=1,
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical host alias",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="HistoricalKeyValue",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                (
                    "hostid_id",
                    models.IntegerField(db_index=True, null=True, blank=True),
                ),
                ("keyid_id", models.IntegerField(db_index=True, null=True, blank=True)),
                ("value", models.CharField(max_length=200, blank=True)),
                ("origin", models.CharField(max_length=200, blank=True)),
                ("createdate", models.DateField(editable=False, blank=True)),
                ("modifieddate", models.DateField(editable=False, blank=True)),
                ("history_id", models.AutoField(serialize=False, primary_key=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        max_length=1,
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical key value",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="HistoricalLinks",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                (
                    "hostid_id",
                    models.IntegerField(db_index=True, null=True, blank=True),
                ),
                ("url", models.CharField(max_length=200)),
                ("tag", models.CharField(max_length=100)),
                ("modifieddate", models.DateField(editable=False, blank=True)),
                ("history_id", models.AutoField(serialize=False, primary_key=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        max_length=1,
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical links",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="HistoricalRestrictedValue",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                ("keyid_id", models.IntegerField(db_index=True, null=True, blank=True)),
                ("value", models.CharField(max_length=200)),
                ("createdate", models.DateField(editable=False, blank=True)),
                ("modifieddate", models.DateField(editable=False, blank=True)),
                ("history_id", models.AutoField(serialize=False, primary_key=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        max_length=1,
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical restricted value",
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name="AllowedKeyAudit",
        ),
        migrations.RemoveField(
            model_name="hostaliasaudit",
            name="hostid",
        ),
        migrations.DeleteModel(
            name="HostAliasAudit",
        ),
        migrations.DeleteModel(
            name="HostAudit",
        ),
        migrations.RemoveField(
            model_name="keyvalueaudit",
            name="hostid",
        ),
        migrations.RemoveField(
            model_name="keyvalueaudit",
            name="keyid",
        ),
        migrations.DeleteModel(
            name="KeyValueAudit",
        ),
        migrations.RemoveField(
            model_name="linksaudit",
            name="hostid",
        ),
        migrations.DeleteModel(
            name="LinksAudit",
        ),
        migrations.RemoveField(
            model_name="restrictedvalueaudit",
            name="keyid",
        ),
        migrations.DeleteModel(
            name="RestrictedValueAudit",
        ),
    ]
