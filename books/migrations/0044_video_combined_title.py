# Generated by Django 4.0.4 on 2022-06-25 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0043_book_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='combined_title',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
