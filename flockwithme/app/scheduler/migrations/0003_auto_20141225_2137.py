# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0002_auto_20141225_2137'),
    ]

    operations = [
        migrations.RenameField(
            model_name='influencer',
            old_name='profiless',
            new_name='profiles',
        ),
    ]
