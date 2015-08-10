from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from catalog.models import Section

# Register your models here.

# admin.site.unregister(User)
# @admin.register(User)
# class UserAdmin(UserAdmin):
#   readonly_fields = ('username', 'last_login', 'date_joined',)
#   fieldsets = [
#     ('User Info', {'fields': [('username', 'is_active',), 'last_login', 'date_joined', 'enrolled_set',]}),
#     ('Personal Info', {'fields': ['first_name', 'last_name', 'email']}),
#   ]
