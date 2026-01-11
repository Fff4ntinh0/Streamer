from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Titles)
admin.site.register(Genres)
admin.site.register(Plans)
admin.site.register(Profile)