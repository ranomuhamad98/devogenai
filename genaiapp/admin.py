from django.contrib import admin

# from genaiapp.views import tasks
from .models import *

# Register your models here.

admin.site.register(Task)
admin.site.register(RightsSupport)