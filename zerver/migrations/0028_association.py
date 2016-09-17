# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0027_auto_20160802_1802'),
    ]

    operations = [
        migrations.CreateModel(
            name='Association',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254, db_index=True)),
                ('account_type', models.CharField(max_length=100)),
                ('account_id', models.CharField(max_length=100)),
            ],
        ),
    ]
