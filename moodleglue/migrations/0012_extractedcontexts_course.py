# Generated by Django 4.1.2 on 2022-11-22 18:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moodleglue', '0011_attachments_extracted_extractedcontexts'),
    ]

    operations = [
        migrations.AddField(
            model_name='extractedcontexts',
            name='course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='moodleglue.course'),
            preserve_default=False,
        ),
    ]
