# -*- coding: utf-8 -*-
from threading import Thread
from django.conf import settings
from flockwithme.app.scheduler.models import OauthSet as AuthSet
from flockwithme.app.scheduler.models import TwitterUser, Job
from flockwithme.core.profiles.models import Profile
import tweepy as Tweepy
from tweepy.error import TweepError
from time import sleep
import time
import datetime
import random
import logging
from .countdown import CountDown
logger = logging.getLogger(__name__)

#pass the tweepy api object 
class AccountFetch(Thread):
	def __init__(self, *args, **kwargs):
		self.jobs = kwargs.pop('jobs')
		self.account = kwargs.pop("account")
		self.queue =  kwargs.pop('queue')
		return super(AccountFetch, self).__init__(*args, **kwargs)
		self.daemon = True
	

	def get_account_info(self, job):
		flock_profile = job.socialprofile
		twitter_instance = flock_profile.handle
		first_query = flock_profile.first_query
		api = self.get_api()
		if first_query == True:
			#api call to get follower count
			twitter_follower_count = api.get_user(screen_name=twitter_instance).followers_count
			flock_profile.twitter_follower_count = twitter_follower_count
			flock_profile.first_query = False
			flock_profile.save()
		elif first_query == False:
			twitter_follower_count = flock_profile.twitter_follower_count
		database_followers = flock_profile.database_follower_count
		if database_followers == None:
			database_followers = 0
		else:
			database_followers = flock_profile.twitter_follower_count
		current_database_ids = [x.twitter_id for x in TwitterUser.objects.all()]
		ids = Tweepy.Cursor(api.followers_ids, screen_name=twitter_instance).items()
		#should_query = [x for x in Tweepy.Cursor(api.followers_ids, screen_name=twitter_instance).items() if x not in current_database_ids]
		#keep grabbing followers while their twitter follower count is bigger than their database follower count
		while database_followers < twitter_follower_count:
			try:
				twitter_id = next(ids)
			except TweepError as e:
				if e.args[0][0]['code'] == 88:
					api = self.get_api()
				elif e.args[0][0]['code'] == 63:
					twitter_id = next(ids)
			except Exception, e:
				print "exception with first try in while loop"
				print e
			else:
				try:
					if twitter_id not in current_database_ids:
						profile = api.get_user(user_id=twitter_id)
						new_twitter_user = TwitterUser.objects.create(screen_name=profile.screen_name, twitter_id=twitter_id, location=profile.location, followers_count=profile.followers_count, friends_count=profile.friends_count, favorites_count = profile.favourites_count)
						new_twitter_user.save()
						get_twitter_user = TwitterUser.objects.get(twitter_id=twitter_id)
						flock_profile.add_follower(get_twitter_user)
						flock_profile.save()
					elif twitter_id in current_database_ids:
						get_twitter_user = TwitterUser.objects.get(twitter_id=twitter_id)
						flock_profile.add_follower(get_twitter_user)
						flock_profile.save()
				except TweepError as e:
					if e.args[0][0]['code']==88:
						self.mark_auth_object_as_rate_limited(api)
						api = self.get_api()
					else:
						time.sleep(2)
					print e

				
		#once all followers are fetched, mark job as complete
		job_id = job.id
		this_job = Job.objects.get(pk=job_id)
		this_job.is_complete = True
		this_job.save()






	#auth_object needs to be a tweepy.api(auth) object
	#OauthSet is a oauthset object from the database
	#calls the countdown()
	#calls mark_auth_object_as_rate_limited()
	#calls the get_api() function
	#return tweepy api object
	def check_rate_limit_status(self, auth_object=None, OauthSet=None):
		if auth_object != None:
			rate_limit_status = int(auth_object.rate_limit_status()['resources']['followers']['/followers/ids']['remaining'])
			try:
				if rate_limit_status == 15:
					return auth_object
				elif rate_limit_status == 1:
					#mark auth_object as rate_limited
					self.mark_auth_object_as_rate_limited(auth_object)
					#get a new auth object
					self.get_api()
				elif rate_limit_status >= 8:
					return auth_object
				else:
					print "else happened on check rate_limit_status"
					
			except Exception, e:
				print "exception with check_rate_limit_status function"
				print e
		elif OauthSet != None:
			#if object is rate limited, call the countdown
			if OauthSet.rate_limited == True:
				self.countdown(OauthSet = OauthSet)
			else:
				pass
		else:
			#fetch all rate_limited objects from the database and call the countdown()
			Rate_Limited_Tokens = AuthSet.objects.filter(rate_limited = True)
			print Rate_Limited_Tokens
			try:
				for Token in Rate_Limited_Tokens:
					self.countdown(OauthSet = Token)
			except Exception, e:
				print "exception with check_rate_limit_status function (else clause)"
				print e


			




	#auth_object needs to be a tweepy.api(auth) object
	#calls the countdown function
	#calls the api function to get a new access token set
	def mark_auth_object_as_rate_limited(self, auth_object):
		try:
			this_access_token = auth_object.rate_limit_status()['rate_limit_context']['access_token']
			print this_access_token
			#get the object using this access token for lookup
			Auth_set = AuthSet.objects.get(access_key=this_access_token)
			Auth_set.rate_limited = True
			Auth_set.save()
			#start the countdown
			countdown = self.countdown(auth_object)
			#get a new api key
			self.get_api()
		except Exception, e:
			print "exception with mark_auth_object_as_rate_limited function"
			print e
	#auth_object needs to be a tweepy.api(auth) object
	#OauthSet needs to be a OauthSet object from the database
	#calls no other functions
	def mark_auth_object_as_ok(self, auth_object=None, OauthSet=None):
		if auth_object != None:
			this_access_token = auth_object.rate_limit_status()['rate_limit_context']['access_token']
			#Get the object using this access token for lookup
			Auth_set = AuthSet.objects.get(access_key=this_access_token)
			Auth_set.rate_limited = False
			Auth_set.save()
			return
		elif OauthSet != None:
			OauthSet.rate_limited = False
			OauthSet.save()

	#auth_object needs to be a tweepy.api(auth) object
	#OauthSet needs to be a rate limited Auth Set object from the database
	#calls the mark_object_as_ok() function
	#checks if a oauth set is still rate limited 
	def countdown(self, auth_object=None, OauthSet=None):
		if auth_object != None:
			this_access_token = auth_object.rate_limit_status()['rate_limit_context']['access_token']
			rate_limited_at = AuthSet.objects.get(access_key = this_access_token).last_used.replace(tzinfo=None)
			time_now = datetime.datetime.utcnow()
			difference = time_now - rate_limited_at
			seconds = difference.seconds
			#once 15 minutes passes (900 seconds, change the oauth_key to OK)
			try:
				if seconds >= 900:
					ok = self.mark_auth_object_as_ok(auth_object)
					return
				else:
					print "time not up"
					return
			except Exception, e:
				print "exception with countdown function"
				print e
		elif OauthSet != None:
			try:
				rate_limited_at = OauthSet.last_used.replace(tzinfo=None)
				time_now = datetime.datetime.utcnow()
				difference = time_now - rate_limited_at
				seconds = difference.seconds
				print seconds
				if seconds >= 900:
					ok = self.mark_auth_object_as_ok(OauthSet=OauthSet)
					return
				else:
					print "time not up"
					return
			except Exception, e:
				print "exception wiht Count Down function elif OauthSet"
				print e


	#calls check_rate_limit_status()
	#calls check_cooldown()
	def get_api(self):
		#check the status of our access tokens on cooldown
		self.check_rate_limit_status()
		try:
			authset = AuthSet.objects.filter(rate_limited = False, active = False)[0]
			consumer_key =str(authset.c_key)
			consumer_secret = str(authset.c_secret)
			auth_token = str(authset.access_key)
			auth_secret = str(authset.key_secret)
			auth = Tweepy.OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(auth_token, auth_secret)
			api = Tweepy.API(auth)
			rate_limit_status = self.check_rate_limit_status(auth_object=api)
			return api
		except Exception, e:
			print "exception with get_api function"
			print e
	
	def lookup_id(self, job):
		twitter_user_id = job.twitter_user.id
		api = self.get_api()
		lookup_twitter_user = api.get_user(user_id=twitter_user_id)
		follower_count = lookup_twitter_user.followers_count
		screen_name = lookup_twitter_user.screen_name
		location = lookup_twitter_user.location
		favorites_count = lookup_twitter_user.favourites_count
		object_ = TwitterUser.objects.get(pk=twitter_user_id)
		object_.favorites_count = favorites_count
		object_.location = location
		object_.screen_name = screen_name
		object_.follower_count = follower_count
		object_.save()




	def run(self):
		for job in self.jobs:
			if job.action == "GET_ACCOUNT_INFO":
			   job.action = self.get_account_info(job)
			elif job.action == "GET_LISTS":
				job.action = self.get_lists()
			elif job.action == "LOOKUP_ID":
				job.action = self.lookup_id(job)




			
		


	


		