# -*- coding: utf-8 -*-
import tweepy	
from threading import Thread
from django.conf import settings
from .models import *
from flockwithme.core.profiles.models import SocialProfile
from django.db.models import Q
from time import sleep
from flockwithme.app.scheduler.models import TwitterList, TwitterUser, OauthSet, TwitterRelationship, list_owner
import random
from tweepy.error import TweepError
import logging
logger = logging.getLogger(__name__)


class JobExecuter(Thread):
	def __init__(self, lock=None, *args, **kwargs):
		self.queue = kwargs.pop('queue')
		self.account = kwargs.pop('account')
		self.jobs = kwargs.pop('jobs')
		self.lock = lock
		try:
			if self.jobs.filter(action="TRACK_FOLLOWERS").count() == 0:
				"print sleep on start"
				self.sleep_on_start()
			else:
				pass
		except tweepy.TweepError as e:
			print "tweep error"
			logger.error("\nUSER: %s, ERROR: %s" % (self.account.handle, e))
			self.queue.put(self)
		return super(JobExecuter, self).__init__(*args, **kwargs)
		self.daemon = True
		self.api = self.get_api()

	def sleep_action(self):
		sleep(random.randint(10,60))

	def sleep_on_start(self):
		sleep(random.randint(1,2))

	

	def auto_follow(self, job):
		statuses = job.hashtag.statuses.all().exclude(twitter_user__twitter_id__in=[x.twitterUser.twitter_id for x in self.account.get_friends()])[0:(job.number*10)]
		users = list(set([status.twitter_user for status in statuses][0:job.number]))
		for user in users:
			try:
				self.api.create_friendship(user.twitter_id, follow=False)
				self.account.add_friend(user)
				self.sleep_action()
			except tweepy.TweepError as e:
				if self.handle_error(e):
					break

		self.account.save()
	#Run once a user adds a new socialmedia account
	#This function will changes if we ever support Instagram, or Pinterest
	def follow_set_account(self, job):
		should_follow = ['jkol36', 'realflockwithme', 'martolini', 'glidewithus']
		socialprofile = job.socialprofile
		api = self.get_api()
		for profile in should_follow:
			api.create_friendship(profile)
		this_job = job.id
		Job.objects.delete(this_job)
			
		
	def unfollow_back(self, job):
		api = self.get_api()
		profile_instance = job.socialprofile
		twitter_screen_name = profile_instance.handle
		followers = set(api.followers_ids(screen_name=twitter_screen_name))
		following = set(api.friends_ids(screen_name=twitter_screen_name))
		should_unfollow = followers - following
		
		for profile in should_unfollow:
			try:
				api.destroy_friendship(profile)
				print 'successfully unfollowed %d' %(profile)
				twitterUser, _ = TwitterUser.objects.get_or_create(twitter_id=profile)
				self.account.add_unfriend(twitterUser)
			except TweepError as e:
				if e.args[0][0]['code']==88:
					self.sleep_action()
				else:
					self.sleep_action()
			except Exception, e:
				print "exception with unfollow_back function"
				print e
		job_id = job.id
		this_job = Job.objects.get(pk=job_id)
		this_job.is_complete = True
		this_job.save()
		self.account.save()
		

	def unfollow_all(self, job):
		unfollowed = 0
		friends = set(self.api.friends_ids())
		for profile in friends:
			try:
				if unfollowed < 3:
					twitterUser, _ = TwitterUser.objects.get_or_create(twitter_id=profile)
					self.api.destroy_friendship(profile)
					print "successfully unfollowed %d " %(profile)
					unfollowed += 1
					self.account.add_unfriend(twitterUser)
			except Exception, e:
				slogger.error(e)
				break
				self.sleep_status()
		
		self.account.save()
	def get_twitter_id(self, job, screen_name):
		twitter_id = self.api.get_user(screen_name=screen_name)
		return twitter_id

	def auto_favorite(self, job):
		for status in job.hashtag.statuses.all().exclude(twitter_id__in=[x.twitterStatus.twitter_id for x in self.account.get_favorites()])[0:job.number]:
			try:
				self.api.create_favorite(status.twitter_id)
				self.account.add_favorite(status)
				self.sleep_action()
			except tweepy.TweepError as e:
				try:
					code = int(e.args[0][0]['code'])
				except:
					break
				if code == 139:
					self.account.add_favorite(status)
				if self.handle_error(e):
					break

		self.account.save()
	def get_profile_instance(self, profile_id):
		twitter_profile = Profile.objects.get(pk=profile_id)
		if twitter_profile:
			return twitter_profile
		else:
			return None
	def get_twitter_user_instance(self, screen_name, twitter_id=False):
		if twitter_id == False:
			user = TwitterUser.objects.get(screen_name=screen_name)
			if user:
				user.is_queried = True
				user.save()
				return user
			else:
				return None
		elif twitter_id != False:
			user = TwitterUser.objects.get(twitter_id=twitter_id)
			if user:
				user.is_queried = True
				user.save()
				return user
			else:
				return None
	def get_lists(self, job):
		job_id = job.id
		account = self.account
		list_owners = job.owner.split(',')
		profile_id = job.socialprofile.profile_id
		profile = self.get_profile_instance(profile_id)
		api = self.get_api()
		for owner in list_owners:
			list_owner_object = list_owner.objects.get(screen_name=owner)
			all_lists = api.lists_all(screen_name=owner)
			for l in all_lists:
				try:
					if l:
						twitter_list, _ = TwitterList.objects.get_or_create(name=l.name, twitter_id = l.id, profile=profile, owner=list_owner_object)
						twitter_list.save()
						if _:
							twitter_list = TwitterList.objects.get(twitter_id=l.id)
							Job.objects.create(socialprofile=self.account, action="GET_LIST_SUBSCRIBERS", twitter_list=twitter_list)
						elif twitter_list:
							Job.objects.create(socialprofile=self.account, action="GET_LIST_SUBSCRIBERS", twitter_list=twitter_list)
						else:
							self.sleep_action()
				except Exception, e:
					print "exception in get_lists function in job executor"
					print e
			
		this = Job.objects.get(pk=job_id)
		this.is_complete = True
		this.save()
		self.sleep_action()


	def get_list_subscribers(self, job):
		job_id = job.id
		list_instance = job.twitter_list
		list_name = job.twitter_list.name.split(',')
		list_owner = job.twitter_list.owner
		twitter_list_id = job.twitter_list.twitter_id
		api = self.get_api()
		for name in list_name:
			print name
			twitter_list_name = name
			list_instance = list_instance
			owner = list_owner
			subscribers = api.list_members(list_id=twitter_list_id)
			for subscriber in subscribers:
				try:
					screen_name = subscriber.screen_name
					twitter_id = subscriber.id
					followers_count = subscriber.followers_count
					location = subscriber.location
					twitter_user, created = TwitterUser.objects.get_or_create(screen_name=screen_name, twitter_id=twitter_id, followers_count=followers_count, location=location)
					twitter_user.save()
					twitter_user = TwitterUser.objects.get(pk=twitter_id)
					new_relationship, created = TwitterRelationship.objects.get_or_create(twitterUser=twitter_user, action="SUBSCRIBE", twitterList=list_instance)
					relationship_id = new_relationship.id
					new_relationship.save()
					get_relationship = TwitterRelationship.objects.get(pk=relationship_id)
					add_subscriber = twitter_user.twitterrelationship_set.add(get_relationship, 'SUBSCRIBE')
					add_subscriber.save()
				except Exception, e:
					print "exception in get_list_subscribers"
					print e
		this_job = Job.objects.get(pk=job_id)
		this_job.is_complete=True
		this_job.save()

			
	def follow_influencer(self, job):
		screen_names = []
		screen_names_in_jobs = job.influencer.screen_name
		screen_names.append(screen_names_in_jobs)
		for screen_name in screen_names:
			twitter_id= self.get_api().get_user(screen_name =screen_name).id
			followers = self.get_api().followers_ids(id =twitter_id)
			try:
				for follower in followers:
					twitterUser, _ = TwitterUser.objects.get_or_create(twitter_id=follower)
					self.get_api().create_friendship(follower)
					self.account.add_friend(twitterUser)
					self.sleep_action()
			except Exception, e:
				print e 
		job_id = job.id
		this_job = Job.objects.get(pk=job_id)
		this_job.is_complete= True
		this_job.save()
		self.account.save()

	def get_api(self):
		auth = tweepy.OAuthHandler(settings.TWITTER_KEY, settings.TWITTER_SECRET)
		auth.set_access_token(self.account.token, self.account.secret)
		return tweepy.API(auth)
	def request_api(self):
		api_objects = OauthSet.objects.filter(active=False, rate_limited=False)
		for api_object in api_objects:
			access_key = api_object.access_key
			access_token_secret = api_object.key_secret
			consumer_key = api_object.c_key
			consumer_secret = api_object.c_secret
			auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(access_key, access_token_secret)
		return tweepy.API(auth)

	def track_followers(self, job, should_dm=False):
		if job.number != 1:
			try:
				dm_job = self.account.jobs.get(action="AUTO_DM")
				should_dm = True
			except:
				should_dm = False
		current_follower_ids = [f.twitterUser.twitter_id for f in self.account.get_followers()]
		ids =  tweepy.Cursor(self.api.followers_ids).items()
		new_followers = []
		while True:
			try:
				twitter_id = next(ids)
				if twitter_id in current_follower_ids:
					return
				with self.lock:
					twitterUser, _ = TwitterUser.objects.get_or_create(twitter_id=twitter_id)
					self.account.add_follower(twitterUser, is_initial = job.number == 1)
				new_followers.append(twitterUser)
			except StopIteration:
				break
			except tweepy.TweepError as e:
				if e.args[0][0]['code'] == 88:
					sleep(60*15)
				elif self.handle_error(e):
					return
		if should_dm:
			for user in new_followers:
				try:
					self.api.send_direct_message(user_id=user.twitter_id, message=dm_job.message)
					self.account.add_dm(user, dm_job.message)
				except tweepy.TweepError as e:
					if self.handle_error(e):
						return
		if job.number == 1:
			job.number = 0
			job.save()
	def follow_list_members(self, job):
		twitter_list_id = job.twitter_list.id
		subscribers = [x for x in TwitterList.objects.get(pk=twitter_list_id).get_list_subscribers()]
		


	def run(self):
		## SETTING THE NUMBER OF HASHTAGS ##
		DAILY_FAV_LIMIT = 500.0
		favs = self.jobs.filter(action="FAVORITE")
		for fav in favs:
			fav.number = int(DAILY_FAV_LIMIT/favs.count())
			fav.save()
		DAILY_FOL_LIMIT = 300.0
		fols = self.jobs.filter(Q(action="FOLLOW_HASHTAG")| Q(action="FOLLOW_INFLUENCER") | Q(action="FOLLOW_MEMBERS_OF_A_LIST"))
		for fol in fols:
			fol.number = int(DAILY_FOL_LIMIT/fols.count())
			fol.save()
		## END NUMBERSETTING
		for job in self.jobs:
			if job.action == 'FOLLOW_HASHTAG':
				if job.is_complete == False:
					job.action = self.auto_follow
					job.action(job)
			elif job.action == 'FAVORITE':
				if job.is_complete==False:
					job.action = self.auto_favorite
					job.action(job)
			elif job.action == 'FOLLOW_INFLUENCER':
				if job.is_complete == False:
					job.action = self.follow_influencer
					job.action(job)
			elif job.action == 'TRACK_FOLLOWERS':
				job.action = self.track_followers
				job.action(job)
			elif job.action == 'UNFOLLOW_BACK':
				if job.is_complete == False:
					job.action = self.unfollow_back
					job.action(job)
			elif job.action =="UNFOLLOW_ALL":
				job.action = self.unfollow_all
				job.action(job)
			elif job.action == "GET_TWITTER_ID":
				job.action = self.get_twitter_id
				job.action(job)
			elif job.action =="GET_LISTS":
				if job.is_complete == False:
					job.action = self.get_lists
					job.action(job)
			elif job.action == "GET_LIST_SUBSCRIBERS":
				if job.is_complete == False:
					job.action = self.get_list_subscribers
					job.action(job)
			elif job.action ==  "GET_ACCOUNT_INFO":
				if job.is_complete == False:
					job.action = self.get_followers(job)
			elif job.action == "FOLLOW_MEMBERS_OF_A_LIST":
				if job.is_complete == False:
					print job
					job.action = self.follow_list_members(job)
			
			#logger.error("\nUSER: %s, ERROR: %s" % (self.account.handle, e))
		self.queue.put(self)

	def handle_error(self, e):
		try:
			code = int(e.args[0][0]['code'])
		except:
			logger.error("\nUSER: %s, ERROR: %s" % (self.account.handle, e))
			return True
		if code == 64:
			logger.error('\nUSER: %s, ERROR: User is suspended' % self.account.handle)
			return True
		if code == 32:
			logger.error('\nUSER: %s, ERROR: Page does not exist' % self.account.handle)
			return False
		if code == 88:
			logger.error('\nUSER: %s, ERROR: Rate limit exceeded' % self.account.handle)
			return True
		if code == 89:
			logger.error('\nUSER: %s, ERROR: Expired token' % self.account.handle)
			return True
		if code == 130:
			logger.error('\nUSER: %s, ERROR: Over capacity' % self.account.handle)
			return True
		if code == 131:
			logger.error('\nUSER: %s, ERROR: Twitters internal error' % self.account.handle)
			return True
		if code == 161:
			logger.error('\nUSER: %s, ERROR: You are unable to follow more people at the time' % self.account.handle)
			return True
		if code == 179:
			logger.error('\nUSER: %s, ERROR: You can not see this tweet, private user probably' % self.account.handle)
			return False
		if code == 185:
			logger.error('\nUSER: %s, ERROR: Cant tweet more, daily status limit reached' % self.account.handle)
			return True
		if code == 187:
			logger.error('\nUSER: %s, ERROR: Status is a duplicate' % self.account.handle)
			return False
		if code == 215:
			logger.error('\nUSER: %s, ERROR: Can not authenticate' % self.account.handle)
			return False