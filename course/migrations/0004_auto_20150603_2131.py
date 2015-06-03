# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20150602_2007'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemFile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('file_title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemFile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('submitted_file', models.FileField(upload_to='')),
                ('prob_file', models.ForeignKey(to='course.ProblemFile')),
            ],
        ),
        migrations.AddField(
            model_name='problem',
            name='problem_files',
            field=models.ManyToManyField(to='course.ProblemFile'),
        ),
        migrations.AddField(
            model_name='studentsolution',
            name='submitted_files',
            field=models.ManyToManyField(to='course.StudentProblemFile'),
        ),
    ]
