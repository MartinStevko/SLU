from django.contrib import admin

from .models import News, Section, Message, Organizer

admin.site.register(News)
admin.site.register(Section)
admin.site.register(Message)
admin.site.register(Organizer)
