# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0010_auto_20150626_1850'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='solution',
        ),
        migrations.RemoveField(
            model_name='problemsolutionfile',
            name='solution',
        ),
        migrations.AddField(
            model_name='problemsolutionfile',
            name='comment',
            field=models.CharField(null=True, max_length=200),
        ),
        migrations.AddField(
            model_name='problemsolutionfile',
            name='problem',
            field=models.ForeignKey(to='course.Problem', null=True),
        ),
        migrations.DeleteModel(
            name='ProblemSolution',
        ),
    ]
