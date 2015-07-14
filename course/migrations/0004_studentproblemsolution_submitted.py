# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20150711_0003'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentproblemsolution',
            name='submitted',
            field=models.DateTimeField(verbose_name='date submitted', null=True),
        ),
    ]
