from django import forms
from .models import SocialProfile, Profile
from flockwithme.app.scheduler.models import Job
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class ProfileCreationForm(UserCreationForm):
	name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Full Name'}))
	email = forms.EmailField(required=True)
	username = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Username'}))
	password1 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password'}))
	password2 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password again'}))
 
	class Meta:
		fields = ['email', 'username', 'password1', 'password2']
		model = Profile

	def clean_username(self):
		username = self.cleaned_data["username"]
		try:
			Profile.objects.get(username=username)
		except Profile.DoesNotExist:
			return username
		raise forms.ValidationError(self.error_messages['duplicate_username'])
	def clean_password(self):
		password1 = self.cleaned_data['password1']
		password2 = self.cleaned_date['password2']
		if password1 != password2:
			return HttpResponse("passwords do not match")
			raise forms.ValidationError(self.error_messages["password's do not match"])
		else:
			pass	
	def save(self, *args, **kwargs):
		profile = super(ProfileCreationForm, self).save(*args, **kwargs)
		name = self.cleaned_data.get('name').split(' ', 1)
		profile.first_name = name[0]
		profile.last_name = name[1] if len(name) > 1 else ''
		profile.save()
		return profile


class SocialProfileCreationForm(forms.ModelForm):
	provider = forms.CharField(required=True)
	token = forms.CharField(required=True)
	secret = forms.CharField(required=True)
	handle = forms.CharField(required=True)
	class Meta:
		model = SocialProfile
		fields = ['provider', 'token', 'secret', 'handle']


	def __init__(self, profile, *args, **kwargs):
		self.profile = profile
		return super(SocialProfileCreationForm, self).__init__(*args, **kwargs)

	def is_valid(self):
		valid = super(SocialProfileCreationForm, self).is_valid()
		if not valid:
			return valid
		if SocialProfile.objects.filter(profile=self.profile, handle=self.cleaned_data.get('handle'), provider=self.cleaned_data.get('provider')).count() > 0:
			return False
		return True



	def save(self, *args, **kwargs):
		kwargs['commit'] = False
		socialprofile = super(SocialProfileCreationForm, self).save(*args, **kwargs)
		socialprofile.profile = self.profile
		socialprofile.save()
		get_id = socialprofile.id
		get_social_profile = SocialProfile.objects.get(pk=get_id)
		new_get_account_info_job = Job.objects.create(socialprofile=get_social_profile, action="GET_ACCOUNT_INFO")
		new_get_account_info_job.save()

		return socialprofile


class ContactForm(forms.ModelForm):
	pass
