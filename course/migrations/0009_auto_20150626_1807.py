# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_auto_20150626_1803'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='problemset',
            name='ps_slug',
        ),
    ]
