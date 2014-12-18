# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0005_auto_20141217_1237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='list_owner',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='list_owner',
            name='twitter_list',
        ),
        migrations.AlterField(
            model_name='twitterlist',
            name='owner',
            field=models.ForeignKey(related_name='Twitter_List_Owner', default=None, to='scheduler.TwitterUser'),
            preserve_default=True,
        ),
    ]
