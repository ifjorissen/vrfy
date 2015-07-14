# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import course.models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_auto_20150713_2213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='grade_script',
            field=models.FileField(upload_to=course.models.solution_file_upload_path),
        ),
    ]
