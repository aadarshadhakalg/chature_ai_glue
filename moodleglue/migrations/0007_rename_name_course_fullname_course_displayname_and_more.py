# Generated by Django 4.1.2 on 2022-11-13 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moodleglue', '0006_rename_processed_discussionslog_replied_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='name',
            new_name='fullname',
        ),
        migrations.AddField(
            model_name='course',
            name='displayname',
            field=models.CharField(default='sdf', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='shortname',
            field=models.CharField(default='dfd', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='summary',
            field=models.TextField(default='fdf'),
            preserve_default=False,
        ),
    ]
