# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_auto_20160105_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problemresult',
            name='job_id',
            field=models.IntegerField(verbose_name='Tango Job ID', blank=True, null=True),
        ),
    ]
