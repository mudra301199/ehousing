from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_title = 'House'
admin.site.site_header = 'House'

my_models = (UserRole, Master, Profile, Visitor, Watchman)
for model in my_models:
    admin.site.register(model)