# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_auto_20150603_2131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='problem_files',
        ),
        migrations.AddField(
            model_name='problemfile',
            name='problem',
            field=models.ForeignKey(null=True, to='course.Problem'),
        ),
    ]
