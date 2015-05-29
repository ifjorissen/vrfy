# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('course', models.CharField(max_length=200)),
                ('statement', models.TextField()),
                ('assigned', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ProblemSet',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('pub_date', models.DateTimeField(verbose_name='date assigned')),
                ('due_date', models.DateTimeField(verbose_name='date due')),
                ('problems', models.ManyToManyField(to='course.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemSolution',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('solution', models.TextField()),
                ('problem', models.ForeignKey(to='course.Problem')),
            ],
        ),
    ]
