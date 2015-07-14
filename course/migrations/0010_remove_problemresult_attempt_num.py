# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_auto_20150714_1827'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemresult',
            name='attempt_num',
        ),
    ]
