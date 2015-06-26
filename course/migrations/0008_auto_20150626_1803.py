# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_auto_20150626_1759'),
    ]

    operations = [
        migrations.RenameField(
            model_name='problemset',
            old_name='slug',
            new_name='ps_slug',
        ),
    ]
