from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()

class RegisterUserForm(UserCreationForm):
	'''
	Form to create a new user
	'''
	first_name = forms.CharField(label='First Name', max_length=300, required=True,
		widget=forms.TextInput(attrs={'autofocus': 'autofocus', 'class': 'form-control'}))
	last_name = forms.CharField(label='Last Name', max_length=300, required=True,
		widget=forms.TextInput(attrs={'autofocus': 'autofocus', 'class': 'form-control'}))
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.',
		widget=forms.TextInput(attrs={'autofocus': 'autofocus', 'class': 'form-control'}))
	password1 = forms.CharField(label="Password", max_length=300, required=True,
		widget=forms.PasswordInput(attrs={'autofocus': 'autofocus', 'class': 'form-control'}))
	password2 = forms.CharField(label="Repeat Password", max_length=300, required=True,
		widget=forms.PasswordInput(attrs={'autofocus': 'autofocus', 'class': 'form-control'}))
	
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

class UserAuthForm(forms.Form):
	'''
	Form to autheticate users
	'''
	username = forms.CharField(max_length=254, help_text='Required. Valid Username.',
		widget=forms.TextInput(attrs={'autofocus': 'autofocus', 'class': 'form-control'}))
	password = forms.CharField(label="Password", max_length=300, required=True,
		widget=forms.PasswordInput(attrs={'autofocus': 'autofocus', 'class': 'form-control'}))
	
	class Meta:
		model = User
		fields =('username', 'password')