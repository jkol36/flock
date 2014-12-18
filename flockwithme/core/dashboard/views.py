from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import tweepy
from django.conf import settings

@login_required
def index(request):
	new_followers, days, potential_customers = 0, 0, 0
	now = timezone.now()
	for acc in request.user.accounts.all():
		follower_count = get_follower_count(request)
		unfollow_count = get_unfollow_count(request)
		new_followers += acc.get_followers(is_initial=False).count()
		potential_customers += (acc.get_friends().count() + acc.get_favorites().count())
		days += ( now - acc.profile.date_joined).days
	money_saved = 100 * days
	return render(request, 'dashboard.jade', {
		'new_followers': new_followers, 
		'potential_customers': potential_customers,
		'money_saved': money_saved,
		'follower_count': follower_count,
		'unfollow_count': unfollow_count,
		})
@login_required

def help(request):
	return render(request, 'help.jade')

def get_follower_count(self):
	accounts = self.user.accounts.all()
	pk=accounts[0].id
	account = self.user.accounts.get(pk=pk)
	token = account.token
	secret = account.secret
	consumer_key, consumer_secret, access_key, access_secret = token, secret, settings.TWITTER_KEY, settings.TWITTER_SECRET
	auth = tweepy.OAuthHandler(access_key, access_secret)
	auth.set_access_token(token, secret)
	api = tweepy.API(auth)
	follower_count = api.me().followers_count
	return follower_count

def get_unfollow_count(self):
	profiles = self.user.accounts.all()
	unfriended = [len(x.get_unfriended()) for x in profiles]
	total = unfriended[0] + unfriended[1]
	return total