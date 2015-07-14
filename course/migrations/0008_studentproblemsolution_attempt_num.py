# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_auto_20150713_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentproblemsolution',
            name='attempt_num',
            field=models.IntegerField(default=0),
        ),
    ]
