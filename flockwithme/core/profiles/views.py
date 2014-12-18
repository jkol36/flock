from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from .forms import ContactForm
from django.contrib.auth import logout
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from flockwithme.app.scheduler.models import Hashtag, Location, Influencer, TwitterList, TwitterUser, Job, list_owner
from flockwithme.core.profiles.models import SocialProfile
from flockwithme.app.scheduler.forms import HashtagForm, LocationForm, InfluencerForm
from django.contrib import messages
import tweepy
from django.conf import settings
import json

def my_accounts(request):
	return render(request, 'my_accounts.jade')

def help(request):
	return render(request, 'help.jade')

class ContactFormView(FormView):
    form_class = ContactForm

    def form_valid(self, form):
        form.save()
        return super(ContactFormView, self).form_valid(form)

    def get_form_kwargs(self):
        # ContactForm instances require instantiation with an
        # HttpRequest.
        kwargs = super(ContactFormView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_success_url(self):
        # This is in a method instead of the success_url attribute
        # because doing it as an attribute would involve a
        # module-level call to reverse(), creating a circular
        # dependency between the URLConf (which imports this module)
        # and this module (which would need to access the URLConf to
        # make the reverse() call).
        return reverse('contact_form_sent')

def my_hashtags(request):
	if request.POST:
		hashtag_name = request.POST.get("hashtag_name").split(',')
		should_add = [x for x in hashtag_name if x not in request.user.hashtags.all()]
		should_delete = [x for x in request.user.hashtags.all() if x not in hashtag_name]
		for name  in should_add:
			hashtag, _ = Hashtag.objects.get_or_create(name=name.lstrip('#').lower())
			hashtag.profiles.add(request.user)
			hashtag.save()
		for name in should_delete:
			hashtag, _ = Hashtag.objects.get_or_create(name=name)
			hashtag.profiles.remove(request.user)
			hashtag.save()

	return render(request, "my_hashtags.jade", {'hashtags':','.join([x.name for x in request.user.hashtags.all()])})	
	


def my_locations(request):
	if request.POST:
		form = LocationForm(request.user, request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Locations updated!")
		else:
			messages.error(request, "Uh Oh. Something went wrong on our end. Feel free to harrass Jon.")
			print form.errors

		
	accounts = request.user.accounts.all()
	pk = accounts[0].id
	return render(request, 'my_locations.jade', {
		'locations': ','.join([x.name for x in request.user.locations.all()]),
		'all_locations': json.dumps([x.name for x in Location.objects.filter(profiles__isnull=False)])
		})

	messages.error(request, "Please add a Twitter Account First")
	return redirect("my_accounts")
	
	


def my_influencers(request):
		if request.POST:
			social_profile = SocialProfile.objects.filter(profile=request.user)[0]
			influencers = request.POST.get('influencers').split(',')
			form = InfluencerForm(request.user, request.POST)
			if form.is_valid():
				form.save()
				for influencer in influencers:
					influencer_object = Influencer.objects.get(screen_name=influencer)
					new_job, created = Job.objects.get_or_create(action="FOLLOW_INFLUENCER", socialprofile=social_profile, influencer=influencer_object)
					new_job.save()
				messages.success(request, "Influencers updated")
			else:
				messages.error(request, "Uh oh, something went wrong on our end. Feel free to harrass Jon.")
		try:
			accounts = request.user.accounts.all()
			pk=accounts[0].id
		 	return render(request, 'influencers.jade', { 'influencers': ','.join([x.screen_name for x in request.user.influencers.all()]),
			'all_influencers': json.dumps([x.screen_name for x in Influencer.objects.filter(profiles__isnull=False)])
			})
		except Exception, e:
			messages.error(request, "Please add a Twitter Account First.")
			return redirect("my_accounts")
	
	
def has_lists(twitter_user_instance):
	query = twitter_user_instance

def api(self):
	accounts = self.user.accounts.all()
	pk=accounts[0].id
	account = self.user.accounts.get(pk=pk)
	token = account.token
	print token
	secret = account.secret
	print secret
	consumer_key, consumer_secret, access_key, access_secret = token, secret, settings.TWITTER_KEY, settings.TWITTER_SECRET
	auth = tweepy.OAuthHandler(access_key, access_secret)
	auth.set_access_token(token, secret)
	api = tweepy.API(auth)
	return api

def get_account_id(self):
	accounts = self.accounts.all()
	account = accounts[0].id
	return account

def get_account(self):
	accounts = self.accounts.all()
	account = accounts[0]
	return account
def get_twitter_user_instance(Screen_Name):
	twitter_user_instance = TwitterUser.objects.get(screen_name=Screen_Name)
	try:
		return twitter_user_instance
	except Exception, e:
		print e
		return None

def get_twitter_list_instance(TwitterUser, *args, **kwargs):
	profile = args.pop['profile']
	if profile:
		print profile
	else:
		twitter_list = TwitterList.objects.filter(owner=TwitterUser)
		if twitter_list:
			return twitter_list
		else:
			return None
def twitter_list_through_profile(Profile):
	twitter_list = TwitterList.objects.filter(profile=Profile)
	if twitter_list:
		return [x.owner for x in twitter_list]
	else:
		return None
def create_twitter_list(name, profile, owner, twitter_id):
	twitter_list = TwitterList.objects.create(name=name, profile=profile, owner=owner, twitter_id = twitter_id)
	return twitter_list

def create_twitter_user(screen_name, twitter_id):
	twitter_user, created = TwitterUser.objects.get_or_create(screen_name=screen_name, twitter_id=twitter_id)
	return twitter_user

def my_lists(request):
	if request.POST:
		socialprofile = SocialProfile.objects.filter(profile=request.user)[0]
		list_owners = request.POST.get('TwitterListOwner').split(',')
		for name in list_owners:
			should_add = [x for x in list_owners if x not in request.user.list_owners.all()]
			should_delete = [x for x in request.user.list_owners.all() if x not in list_owners]
		for name in should_add:
			new_list_owner, created = list_owner.objects.get_or_create(screen_name=name.lstrip(',').lower())
			new_list_owner.profile.add(request.user)
			new_list_owner.save()
			new_job, created = Job.objects.get_or_create(action="GET_LISTS", owner=name, socialprofile=socialprofile)
			new_job.save()
		for name in should_delete:
			new_list_owner, created = list_owner.objects.get_or_create(screen_name=name)
			new_list_owner.profile.remove(request.user)
			new_list_owner.save()
	
		
	return render(request, 'my_lists.jade', {'list_owner':','.join([str(x.screen_name) for x in list_owner.objects.filter(profile=request.user)]),
		'all_list_owners': json.dumps([x.name for x in TwitterList.objects.all()]), "twitter_lists":TwitterList.objects.filter(profile=request.user), 'list_followers': ','.join([str(x.owner) for x in request.user.twitterlist_set.all()])})

def logout_view(request):
	logout(request)
	return redirect(reverse('landingpage'))
