# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0003_auto_20141225_2137'),
    ]

    operations = [
        migrations.CreateModel(
            name='nigga',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nigga', models.CharField(max_length=250)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='hashtag',
            name='profiles',
        ),
        migrations.RemoveField(
            model_name='influencer',
            name='profiles',
        ),
        migrations.RemoveField(
            model_name='job',
            name='hashtag',
        ),
        migrations.RemoveField(
            model_name='job',
            name='influencer',
        ),
        migrations.DeleteModel(
            name='Influencer',
        ),
        migrations.RemoveField(
            model_name='job',
            name='location',
        ),
        migrations.RemoveField(
            model_name='job',
            name='socialprofile',
        ),
        migrations.RemoveField(
            model_name='job',
            name='twitter_list',
        ),
        migrations.RemoveField(
            model_name='job',
            name='twitter_user',
        ),
        migrations.DeleteModel(
            name='Job',
        ),
        migrations.DeleteModel(
            name='list_owner',
        ),
        migrations.RemoveField(
            model_name='location',
            name='profiles',
        ),
        migrations.DeleteModel(
            name='Location',
        ),
        migrations.DeleteModel(
            name='OauthSet',
        ),
        migrations.RemoveField(
            model_name='twitterlist',
            name='followers',
        ),
        migrations.RemoveField(
            model_name='twitterlist',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='twitterlist',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='twitterlist',
            name='subscribers',
        ),
        migrations.RemoveField(
            model_name='twitterrelationship',
            name='socialProfile',
        ),
        migrations.RemoveField(
            model_name='twitterrelationship',
            name='twitterList',
        ),
        migrations.DeleteModel(
            name='TwitterList',
        ),
        migrations.RemoveField(
            model_name='twitterrelationship',
            name='twitterStatus',
        ),
        migrations.RemoveField(
            model_name='twitterrelationship',
            name='twitterUser',
        ),
        migrations.RemoveField(
            model_name='twitterstatus',
            name='hashtags',
        ),
        migrations.DeleteModel(
            name='Hashtag',
        ),
        migrations.RemoveField(
            model_name='twitterstatus',
            name='relationships',
        ),
        migrations.RemoveField(
            model_name='twitterstatus',
            name='twitter_user',
        ),
        migrations.DeleteModel(
            name='TwitterStatus',
        ),
        migrations.RemoveField(
            model_name='twitteruser',
            name='relationships',
        ),
        migrations.DeleteModel(
            name='TwitterRelationship',
        ),
        migrations.DeleteModel(
            name='TwitterUser',
        ),
    ]
