# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_studentproblemsolution_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='grade_script',
            field=models.ForeignKey(related_name='grading', null=True, to='course.ProblemSolutionFile'),
        ),
        migrations.AlterField(
            model_name='problemsolutionfile',
            name='comment',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='studentproblemfile',
            name='attempt_num',
            field=models.IntegerField(default=0),
        ),
    ]
