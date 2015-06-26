# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import course.models


class Migration(migrations.Migration):

    dependencies = [
        ('generic', '0001_initial'),
        ('course', '0006_auto_20150603_2343'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemSolutionFile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('file_upload', models.FileField(upload_to=course.models.solution_file_upload_path)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemSet',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemSolution',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('submitted', models.DateTimeField(verbose_name='date submitted')),
            ],
        ),
        migrations.RenameModel(
            old_name='ProblemFile',
            new_name='RequiredProblemFilename',
        ),
        migrations.RemoveField(
            model_name='studentsolution',
            name='problem',
        ),
        migrations.RemoveField(
            model_name='studentsolution',
            name='ps',
        ),
        migrations.RemoveField(
            model_name='studentsolution',
            name='user',
        ),
        migrations.RemoveField(
            model_name='problemsolution',
            name='solution',
        ),
        migrations.RemoveField(
            model_name='studentproblemfile',
            name='attempt_num',
        ),
        migrations.AddField(
            model_name='problem',
            name='slug',
            field=models.SlugField(unique=True, max_length=60, default=''),
        ),
        migrations.AddField(
            model_name='problemset',
            name='slug',
            field=models.SlugField(unique=True, max_length=60, default=''),
        ),
        migrations.AlterField(
            model_name='studentproblemfile',
            name='solution',
            field=models.ForeignKey(to='course.StudentProblemSolution', null=True),
        ),
        migrations.AlterField(
            model_name='studentproblemfile',
            name='submitted_file',
            field=models.FileField(upload_to=course.models.student_file_upload_path),
        ),
        migrations.DeleteModel(
            name='StudentSolution',
        ),
        migrations.AddField(
            model_name='studentproblemsolution',
            name='problem',
            field=models.ForeignKey(to='course.Problem'),
        ),
        migrations.AddField(
            model_name='studentproblemsolution',
            name='ps',
            field=models.ForeignKey(to='course.ProblemSet'),
        ),
        migrations.AddField(
            model_name='studentproblemsolution',
            name='user',
            field=models.ForeignKey(to='generic.CSUser'),
        ),
        migrations.AddField(
            model_name='studentproblemset',
            name='problem_set',
            field=models.ForeignKey(to='course.ProblemSet'),
        ),
        migrations.AddField(
            model_name='problemsolutionfile',
            name='solution',
            field=models.ForeignKey(to='course.ProblemSolution', null=True),
        ),
    ]
