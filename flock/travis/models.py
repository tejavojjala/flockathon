from __future__ import unicode_literals

from django.db import models

# Create your models here.

class User(models.Model):
	userId = models.CharField(max_length = 100)
	token = models.CharField(max_length = 100)
	userToken = models.CharField(max_length = 100)

class TravisAccountManager(models.Manager):
	def create_travis_account(self,flock_user,github_access_token,github_userId):
		travisAccount = self.create(flock_user=flock_user,github_access_token = github_access_token,github_userId = github_userId)
		return travisAccount

class TravisAccounts(models.Model):
	github_access_token = models.CharField(max_length = 100)
	github_userId = models.CharField(max_length = 100)
	flock_user = models.ForeignKey(User, on_delete=models.CASCADE)
	objects = TravisAccountManager()