from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

# Create your models here.
class CustomBaseUserManager(BaseUserManager):
	'''
	Custom User Manager
	'''
	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		if not email:
			raise ValueError("Email address is required")

		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)

		return user

	def create_user(self, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefaults('is_superuser', False)

		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True')

		return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
	'''
	Abstract to make email the username
	'''
	username = None
	email = models.EmailField(unique=True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name']

	objects = CustomBaseUserManager()

	@property
	def regenerate_api_token(self):
		from rest_framework.authtoken.models import Token
		try:
			token = Token.objects.get(user=self)
			token.delete()
		except Token.DoesNotExist:
			pass
		Token.objects.create(user=self)

	@property
	def get_full_name(self):
		return '{0} {1}'.format(self.first_name, self.last_name)



@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
