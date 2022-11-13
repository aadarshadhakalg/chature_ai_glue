from django.contrib import admin
from .models import DiscussionsLog, Attachments, Course

# Register your models here.
admin.site.register(DiscussionsLog)
admin.site.register(Attachments)
admin.site.register(Course)
