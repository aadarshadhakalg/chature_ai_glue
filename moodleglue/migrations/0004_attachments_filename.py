# Generated by Django 4.1.2 on 2022-11-13 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moodleglue', '0003_discussionslog_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachments',
            name='filename',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]