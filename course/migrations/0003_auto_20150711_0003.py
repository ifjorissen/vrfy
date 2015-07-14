# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_studentproblemfile_attempt_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentproblemset',
            name='submitted',
            field=models.DateTimeField(null=True, verbose_name='date submitted'),
        ),
    ]
