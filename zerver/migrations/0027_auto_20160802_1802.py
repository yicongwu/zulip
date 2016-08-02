# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0026_auto_20160802_1801'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('name', 'owner')]),
        ),
    ]
