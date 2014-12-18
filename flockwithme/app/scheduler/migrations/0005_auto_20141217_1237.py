# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduler', '0004_oauthset_last_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='list_owner',
            name='profile',
            field=models.ManyToManyField(related_name=b'list_owners', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='list_owner',
            name='twitter_list',
            field=models.ManyToManyField(related_name=b'twitter_list', null=True, to='scheduler.TwitterList', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twitterlist',
            name='owner',
            field=models.ForeignKey(related_name=b'Twitter_List_Owner', blank=True, to='scheduler.list_owner', null=True),
        ),
    ]
