# Generated by Django 4.0.4 on 2022-05-06 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0031_alter_wish_remarks'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.CharField(blank=True, max_length=100, null=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('kind', models.CharField(choices=[('MOVIE', 'Movie'), ('MOVIE', 'Cabaret'), ('MOVIE', 'IMDB Top 100'), ('MOVIE', 'Music Video'), ('MOVIE', 'Series'), ('MOVIE', 'StarTrek')], max_length=20)),
                ('season', models.IntegerField(blank=True, null=True)),
                ('episode', models.IntegerField(blank=True, null=True)),
                ('size', models.BigIntegerField(blank=True, null=True)),
            ],
        ),
    ]
