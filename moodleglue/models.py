from django.db import models


# Create your models here.


class Course(models.Model):
    course_id = models.IntegerField(primary_key=True)
    fullname = models.CharField(max_length=500)
    displayname = models.CharField(max_length=255)
    shortname = models.CharField(max_length=100)
    summary = models.TextField()
    timemodified = models.BigIntegerField(default=0)

    def __str__(self):
        return self.displayname


class DiscussionsLog(models.Model):
    id = models.IntegerField(primary_key=True)
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
    answer = models.TextField(null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    replyid = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.subject


class Attachments(models.Model):
    file = models.URLField()
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    filename = models.CharField(max_length=500, null=True, blank=True)
    extracted = models.BooleanField(default=False)

    def __str__(self):
        return self.filename


class ExtractedContexts(models.Model):
    attachment = models.ForeignKey(to=Attachments, on_delete=models.CASCADE)
    topic = models.CharField(max_length=1000)
    page_number = models.CharField(max_length=10)
    index = models.CharField(max_length=1000)
    heading_order = models.CharField(max_length=10)
    content = models.TextField()
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.topic
