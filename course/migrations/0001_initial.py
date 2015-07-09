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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('file_upload', models.FileField(upload_to=course.models.solution_file_upload_path)),
                ('comment', models.CharField(null=True, max_length=200)),
                ('problem', models.ForeignKey(to='course.Problem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequiredProblemFilename',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('file_title', models.CharField(max_length=200)),
                ('problem', models.ForeignKey(to='course.Problem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('submitted_file', models.FileField(upload_to=course.models.student_file_upload_path)),
                ('required_problem_filename', models.ForeignKey(to='course.RequiredProblemFilename', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('submitted', models.DateTimeField(verbose_name='date submitted')),
                ('problem_set', models.ForeignKey(to='course.ProblemSet')),
                ('user', models.ForeignKey(to='generic.CSUser', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemSolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('problem', models.ForeignKey(to='course.Problem')),
                ('student_problem_set', models.ForeignKey(to='course.StudentProblemSet', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='studentproblemfile',
            name='student_problem_solution',
            field=models.ForeignKey(to='course.StudentProblemSolution', null=True),
        ),
    ]
