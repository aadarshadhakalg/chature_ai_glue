# Generated by Django 4.1.2 on 2022-11-13 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moodleglue', '0004_attachments_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussionslog',
            name='answer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='discussionslog',
            name='dislike_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='discussionslog',
            name='like_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='discussionslog',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]
