# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import course.models


class Migration(migrations.Migration):

    dependencies = [
        ('generic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=200)),
                ('course', models.CharField(max_length=200)),
                ('description', models.TextField(default='')),
                ('statement', models.TextField(default='')),
                ('many_attempts', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProblemSet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(default='')),
                ('pub_date', models.DateTimeField(verbose_name='date assigned')),
                ('due_date', models.DateTimeField(verbose_name='date due')),
                ('problems', models.ManyToManyField(to='course.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemSolutionFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('file_upload', models.FileField(upload_to=course.models.solution_file_upload_path)),
                ('comment', models.CharField(max_length=200, null=True)),
                ('problem', models.ForeignKey(to='course.Problem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequiredProblemFilename',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('file_title', models.CharField(max_length=200)),
                ('problem', models.ForeignKey(to='course.Problem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('submitted_file', models.FileField(upload_to=course.models.student_file_upload_path)),
                ('prob_file', models.ForeignKey(to='course.RequiredProblemFilename')),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemSet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('problem_set', models.ForeignKey(to='course.ProblemSet')),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemSolution',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('submitted', models.DateTimeField(verbose_name='date submitted')),
                ('problem', models.ForeignKey(to='course.Problem')),
                ('ps', models.ForeignKey(to='course.ProblemSet')),
                ('user', models.ForeignKey(to='generic.CSUser')),
            ],
        ),
        migrations.AddField(
            model_name='studentproblemfile',
            name='solution',
            field=models.ForeignKey(to='course.StudentProblemSolution', null=True),
        ),
    ]
