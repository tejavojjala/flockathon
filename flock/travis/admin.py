from django.contrib import admin
from travis.models import User,TravisAccounts

# Register your models here.
admin.site.register(User)
admin.site.register(TravisAccounts)
