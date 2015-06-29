# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grade', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assignment',
            old_name='name',
            new_name='public_name',
        ),
        migrations.RenameField(
            model_name='file',
            old_name='destname',
            new_name='dest_name',
        ),
        migrations.RenameField(
            model_name='file',
            old_name='localname',
            new_name='local_name',
        ),
        migrations.AddField(
            model_name='assignment',
            name='tango_name',
            field=models.CharField(max_length=200, editable=False, default='hw1'),
            preserve_default=False,
        ),
    ]
