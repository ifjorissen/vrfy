# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='graderlib',
            name='cs_course',
            field=models.ForeignKey(null=True, verbose_name='Course Name', to='catalog.Course'),
        ),
        migrations.AlterField(
            model_name='problemset',
            name='pub_date',
            field=models.DateTimeField(verbose_name='date assigned', default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='studentproblemsolution',
            name='job_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Tango Job ID'),
        ),
    ]
