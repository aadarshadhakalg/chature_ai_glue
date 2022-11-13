from django.db import models


# Create your models here.


class Course(models.Model):
    course_id = models.IntegerField(primary_key=True)
    fullname = models.CharField(max_length=500)
    displayname = models.CharField(max_length=255)
    shortname = models.CharField(max_length=100)
    summary = models.TextField()


class DiscussionsLog(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    authors_profile = models.URLField(null=False, blank=False)
    authors_name = models.CharField(max_length=255, null=False, blank=False)
    subject = models.CharField(max_length=500, null=False, blank=False)
    reply_subject = models.CharField(max_length=500, null=False, blank=False)
    message = models.TextField()
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE, null=True, blank=True)
    replied = models.BooleanField(default=False)
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    answer = models.TextField(null=True,blank=True)
    updated_on = models.DateTimeField(auto_now=True)


class Attachments(models.Model):
    file = models.URLField()
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    filename = models.CharField(max_length=500, null=True, blank=True)
