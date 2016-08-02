# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import zerver.lib.str_utils


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0025_realm_message_content_edit_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60, db_index=True)),
                ('invite_only', models.NullBooleanField(default=True)),
                ('description', models.CharField(default='', max_length=1024)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('deactivated', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            bases=(zerver.lib.str_utils.ModelReprMixin, models.Model),
        ),
        migrations.AlterField(
            model_name='stream',
            name='invite_only',
            field=models.NullBooleanField(default=True),
        ),
    ]
