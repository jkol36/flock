# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0006_auto_20141218_0008'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='twitter_user',
            field=models.ForeignKey(related_name='twitter_users_in_query', blank=True, to='scheduler.TwitterUser', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='action',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'FOLLOW_HASHTAG', b'Follow users based on hashtags'), (b'FOLLOW_BACK', b'Follow back your followers'), (b'FAVORITE', b'Favorite tweets'), (b'UNFOLLOW_BACK', b"Unfollow all the users that haven't followed you back"), (b'UNFOLLOW_ALL', b'Unfollow everyone you currently follow'), (b'AUTO_DM', b'Send direct messages to your followers'), (b'FOLLOW_INFLUENCER', b'Follow people who follow certain accounts.'), (b'FOLLOW_MEMBERS_OF_LIST', b'Follow the members of a specific list'), (b'TRACK_FOLLOWERS', b'Track followers'), (b'GET_FOLLOWERS', b'get_followers'), (b'GET_LISTS', b'get_lists'), (b'GET_LIST_SUBSCRIBERS', b'get_list_subscribers'), (b'GET_ACCOUNT_INFO', b'get_account_info'), (b'LOOKUP_ID', b'look up twitter ID and get account info')]),
            preserve_default=True,
        ),
    ]
