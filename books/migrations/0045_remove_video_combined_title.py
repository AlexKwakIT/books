# Generated by Django 4.0.4 on 2022-07-07 11:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0044_video_combined_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='combined_title',
        ),
    ]
