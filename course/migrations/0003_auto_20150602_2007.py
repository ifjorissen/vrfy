# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('generic', '0001_initial'),
        ('course', '0002_auto_20150529_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentSolution',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('submitted', models.DateTimeField(verbose_name='date submitted')),
            ],
        ),
        migrations.AddField(
            model_name='problem',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='problem',
            name='many_attempts',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='statement',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='studentsolution',
            name='problem',
            field=models.ForeignKey(to='course.Problem'),
        ),
        migrations.AddField(
            model_name='studentsolution',
            name='ps',
            field=models.ForeignKey(to='course.ProblemSet'),
        ),
        migrations.AddField(
            model_name='studentsolution',
            name='user',
            field=models.ForeignKey(to='generic.CSUser'),
        ),
    ]
