# Generated by Django 4.1.2 on 2022-11-22 06:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('moodleglue', '0010_discussionslog_id_alter_discussionslog_replyid'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachments',
            name='extracted',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ExtractedContexts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=1000)),
                ('page_number', models.CharField(max_length=10)),
                ('index', models.CharField(max_length=1000)),
                ('heading_order', models.CharField(max_length=10)),
                ('content', models.TextField()),
                ('attachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moodleglue.attachments')),
            ],
        ),
    ]