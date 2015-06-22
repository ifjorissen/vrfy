# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_auto_20150603_2225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentsolution',
            name='submitted_files',
        ),
        migrations.AddField(
            model_name='studentproblemfile',
            name='attempt_num',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='studentproblemfile',
            name='solution',
            field=models.ForeignKey(to='course.StudentSolution', null=True),
        ),
    ]
