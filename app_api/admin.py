from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User_data

class User_dataAdmin(UserAdmin):
    list_display = ('username', 'usr_email', 'usr_password', 'is_active', 'is_staff')

# Register your User_data model with the User_dataAdmin class
admin.site.register(User_data, User_dataAdmin)
