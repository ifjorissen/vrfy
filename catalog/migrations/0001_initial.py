# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=200)),
                ('num', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Reedie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('role', models.CharField(max_length=40)),
                ('last_updated', models.DateTimeField(verbose_name='most recent ldap query', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('section_id', models.CharField(max_length=20)),
                ('start_date', models.DateTimeField(verbose_name='course start date')),
                ('end_date', models.DateTimeField(verbose_name='course end date')),
                ('course', models.ForeignKey(to='catalog.Course')),
                ('enrolled', models.ManyToManyField(related_name='enrolled', to='catalog.Reedie')),
                ('prof', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
