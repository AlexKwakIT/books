# Generated by Django 4.0.4 on 2022-06-05 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0037_alter_video_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ['series', 'season', 'title']},
        ),
        migrations.RemoveField(
            model_name='video',
            name='episode',
        ),
        migrations.RemoveField(
            model_name='video',
            name='size',
        ),
        migrations.AddField(
            model_name='video',
            name='quality',
            field=models.CharField(choices=[('UNKNOWN', 'Unknown'), ('UNKNOWN', 'Dvd'), ('UNKNOWN', 'BluRay')], default='UNKNOWN', max_length=20),
        ),
    ]
