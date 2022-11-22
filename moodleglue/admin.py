from django.contrib import admin
from .models import DiscussionsLog, Attachments, Course, ExtractedContexts


class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'authors_name']


class AttachmentsAdmin(admin.ModelAdmin):
    list_display = ['filename', 'file']


class CourseAdmin(admin.ModelAdmin):
    list_display = ['displayname', 'timemodified']


# Register your models here.
admin.site.register(DiscussionsLog, DiscussionAdmin)
admin.site.register(Attachments, AttachmentsAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(ExtractedContexts)
