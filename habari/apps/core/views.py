from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from habari.apps.crawl.models import Article, NewsSource
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as user_login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def index(request):
	sources = NewsSource.objects.order_by('pk')
	return render(request, 'core/index.html', {'sources':sources})

def status(request):
	sources = NewsSource.objects.all().order_by('pk')
	return render(request, 'core/status.html', {'sources':sources})

def get_source(request, source):
	source = source.upper()
	today = timezone.localtime(timezone.now())
	return day(request,source, today.year, today.month,today.day)

def get_author_articles(request, source, author):
	'''
	Get articles belonging to a particular author
	'''
	import re
	source = source.upper()
	author_string = re.sub(r'-',' ',author).upper()  
	news_source = get_object_or_404(NewsSource, slug__iexact=source)
	article_list = Article.objects.filter(news_source=news_source, author__contains=[author_string]).order_by('-publication_date', '-timestamp')

	paginator = Paginator(article_list, 50)
	page = request.GET.get('page')
	try:
		articles = paginator.page(page)
	except PageNotAnInteger:
		articles = paginator.page(1)
	except EmptyPage:
		articles = paginator.page(paginator.num_pages)

	return render(request, 'core/author_articles.html', {'articles':articles, 'source':news_source, 'author':author_string})

def day(request, source, year, month, day):
	'''
	Get articles for a particular day from a particular new source
	'''
	source = source.upper()
	date = datetime(int(year), int(month), int(day))
	source = get_object_or_404(NewsSource, slug__iexact=source)
	article_list = Article.objects.filter(news_source=source, publication_date=date).order_by('-publication_date', '-timestamp')

	paginator = Paginator(article_list, 30)
	page = request.GET.get('page')
	try:
		articles = paginator.page(page)
	except PageNotAnInteger:
		articles = paginator.page(1)
	except EmptyPage:
		articles = paginator.page(paginator.num_pages)
	
	return render(request, 'core/news_source.html', {'articles':articles,'source':source})

def login(request):
	'''
	Functionality to login a user 
	'''
	from .forms import UserAuthForm
	if request.method == 'POST':
		form = UserAuthForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']

			user = authenticate(request, email=email, password=password)
			if user is not None:
				user_login(request, user)
				messages.success(request, f'Welcome back {request.user.first_name} {request.user.last_name}!')
				return redirect('profile')
			else:
				messages.error(
	                request, 'Wrong username and password combination. Please Try Again!')
				return redirect(request.META.get('HTTP_REFERER'))

	else:
		form = UserAuthForm()

	return render(request, 'auth/login.html', {"form": form})

def register(request):
	'''
	Create a new user
	'''
	from .forms import RegisterUserForm
	if request.method == 'POST':
		form = RegisterUserForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data['email']
			password = form.cleaned_data['password1']

			user  = authenticate(request, email=email, password=password)
			if user is not None:
				user_login(request, user)
				messages.success(request, f'Hey there {request.user.first_name} {request.user.last_name}, your new account has been created!')
				return redirect('profile')
	else:
		form = RegisterUserForm()
	return render(request, 'auth/register.html', {'form':form})

@login_required
def profile(request):
	'''
	View an authenticated user's profile
	'''
	from rest_framework.authtoken.models import Token
	try:
		obj = Token.objects.get(user=request.user)
	except Token.DoesNotExist:
		obj = Token.objects.create(user=request.user)
	return render(request, 'core/profile.html', {'obj':obj})