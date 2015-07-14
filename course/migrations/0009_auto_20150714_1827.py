# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('generic', '0001_initial'),
        ('course', '0008_studentproblemsolution_attempt_num'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemResult',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('timestamp', models.DateTimeField(null=True, verbose_name='date received')),
                ('attempt_num', models.IntegerField(default=-1)),
                ('score', models.IntegerField(default=-1)),
                ('external_log', models.TextField(null=True)),
                ('internal_log', models.TextField(null=True)),
                ('sanity_log', models.TextField(null=True)),
                ('raw_log', models.TextField(null=True)),
                ('problem', models.ForeignKey(to='course.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemResultSet',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('problem_set', models.ForeignKey(to='course.ProblemSet')),
                ('sp_set', models.ForeignKey(to='course.StudentProblemSet')),
                ('user', models.ForeignKey(null=True, to='generic.CSUser')),
            ],
        ),
        migrations.AddField(
            model_name='problemresult',
            name='result_set',
            field=models.ForeignKey(to='course.ProblemResultSet'),
        ),
        migrations.AddField(
            model_name='problemresult',
            name='sp_sol',
            field=models.ForeignKey(to='course.StudentProblemSolution'),
        ),
        migrations.AddField(
            model_name='problemresult',
            name='user',
            field=models.ForeignKey(null=True, to='generic.CSUser'),
        ),
    ]
