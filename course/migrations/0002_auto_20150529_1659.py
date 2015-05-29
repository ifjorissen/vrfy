# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='assigned',
        ),
        migrations.AddField(
            model_name='problemset',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
