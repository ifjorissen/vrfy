# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import course.models
import django_markdown.models
import datetime
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraderLib',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lib_upload', models.FileField(verbose_name='Grader Resource', upload_to=course.models.grader_lib_upload_path, max_length=1000)),
                ('comment', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('time_limit', models.IntegerField(verbose_name='Grading Time Limit (seconds)', default=30)),
                ('description', django_markdown.models.MarkdownField(default='', help_text='You can use plain text, markdown, or html for your problem description', blank=True)),
                ('statement', django_markdown.models.MarkdownField(verbose_name='TL;DR', default='', blank=True)),
                ('many_attempts', models.BooleanField(verbose_name='allow multiple attempts', default=True)),
                ('autograde_problem', models.BooleanField(verbose_name='autograde this problem', default=True)),
                ('grade_script', models.FileField(help_text='Upload the script that grades the student submission here', max_length=1000, null=True, upload_to=course.models.grade_script_upload_path, blank=True)),
                ('cs_course', models.ForeignKey(verbose_name='Course Name', null=True, to='catalog.Course')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('job_id', models.IntegerField(verbose_name='Tango Job ID', default=-1)),
                ('attempt_num', models.IntegerField(default=-1)),
                ('timestamp', models.DateTimeField(verbose_name='date received (from Tango)', null=True)),
                ('max_score', models.IntegerField(null=True, blank=True)),
                ('score', models.IntegerField(default=-1)),
                ('json_log', jsonfield.fields.JSONField(verbose_name='Session Log', null=True, blank=True)),
                ('raw_output', models.TextField(verbose_name='Raw Autograder Output', null=True, blank=True)),
                ('problem', models.ForeignKey(to='course.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('description', django_markdown.models.MarkdownField(default='', help_text='Provide some additional information about this problem set.')),
                ('pub_date', models.DateTimeField(verbose_name='date assigned', default=datetime.datetime(2015, 10, 4, 20, 0, 0, 447850, tzinfo=utc))),
                ('due_date', models.DateTimeField(verbose_name='date due')),
                ('cs_section', models.ManyToManyField(verbose_name='course Section', to='catalog.Section')),
                ('problems', models.ManyToManyField(to='course.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemSolutionFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_upload', models.FileField(max_length=1000, help_text='Upload a solution file here', upload_to=course.models.solution_file_upload_path)),
                ('comment', models.CharField(max_length=200, null=True, blank=True)),
                ('problem', models.ForeignKey(to='course.Problem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequiredProblemFilename',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_title', models.CharField(max_length=200, help_text='Use the name of the python file the grader script imports as a module. E.g: main.py if the script imports main')),
                ('force_rename', models.BooleanField(default=True, help_text='Uncheck if file name does not matter')),
                ('problem', models.ForeignKey(to='course.Problem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted_file', models.FileField(max_length=1000, upload_to=course.models.student_file_upload_path)),
                ('attempt_num', models.IntegerField(default=0)),
                ('required_problem_filename', models.ForeignKey(to='course.RequiredProblemFilename', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted', models.DateTimeField(verbose_name='date submitted')),
                ('problem_set', models.ForeignKey(to='course.ProblemSet')),
                ('user', models.ForeignKey(to='catalog.Reedie')),
            ],
        ),
        migrations.CreateModel(
            name='StudentProblemSolution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attempt_num', models.IntegerField(verbose_name='attempts made', default=0)),
                ('submitted', models.DateTimeField(verbose_name='date submitted', null=True)),
                ('job_id', models.IntegerField(verbose_name='Tango Job ID', default=-1)),
                ('problem', models.ForeignKey(to='course.Problem')),
                ('student_problem_set', models.ForeignKey(to='course.StudentProblemSet', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='studentproblemfile',
            name='student_problem_solution',
            field=models.ForeignKey(to='course.StudentProblemSolution', null=True),
        ),
        migrations.AddField(
            model_name='problemresult',
            name='sp_set',
            field=models.ForeignKey(verbose_name='Student Problem Set', to='course.StudentProblemSet'),
        ),
        migrations.AddField(
            model_name='problemresult',
            name='sp_sol',
            field=models.ForeignKey(verbose_name='Student Problem Solution', to='course.StudentProblemSolution'),
        ),
        migrations.AddField(
            model_name='problemresult',
            name='user',
            field=models.ForeignKey(to='catalog.Reedie'),
        ),
    ]
