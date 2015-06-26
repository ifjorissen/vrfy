# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_auto_20150626_1807'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemsolution',
            name='problem',
        ),
        migrations.AddField(
            model_name='problem',
            name='solution',
            field=models.ForeignKey(to='course.ProblemSolution', null=True),
        ),
    ]
