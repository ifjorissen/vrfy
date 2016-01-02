# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problemset',
            name='pub_date',
            field=models.DateTimeField(verbose_name='date assigned', default=django.utils.timezone.now),
        ),
    ]
