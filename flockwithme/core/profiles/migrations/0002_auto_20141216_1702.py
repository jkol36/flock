# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialprofile',
            name='database_follower_count',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='socialprofile',
            name='twitter_follower_count',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
    ]
